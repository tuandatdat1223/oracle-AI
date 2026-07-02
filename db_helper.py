import oracledb
import re
import json
import os
import datetime

def init_db(user, password, host, port, sid):
    try:
        dsn = f"{host}:{port}/{sid}"
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        return conn
    except Exception:
        return None

def check_connection(session_state):
    if "db_conn" in session_state and session_state.db_conn is not None:
        try:
            session_state.db_conn.ping()
            return True
        except Exception:
            pass # Chuyển xuống thử kết nối lại
            
    # Thử tự động kết nối lại hoặc kết nối lần đầu nếu có sẵn thông tin đầy đủ
    if session_state.get("db_user") and session_state.get("db_pass") and session_state.get("db_host") and session_state.get("db_port") and session_state.get("db_sid"):
        conn = init_db(
            session_state.db_user,
            session_state.db_pass,
            session_state.db_host,
            session_state.db_port,
            session_state.db_sid
        )
        if conn:
            session_state.db_conn = conn
            return True
            
    return False

def get_db_schema(conn):
    if conn is None:
        return ""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, column_name, data_type 
            FROM user_tab_columns 
            WHERE table_name NOT LIKE 'BIN$%' AND table_name NOT LIKE 'DR$%'
            ORDER BY table_name, column_id
        """)
        rows = cursor.fetchall()
        
        schema_dict = {}
        for r in rows:
            t, c, d = r[0], r[1], r[2]
            if t not in schema_dict:
                schema_dict[t] = []
            schema_dict[t].append(f"{c}({d})")
            
        schema_text = ""
        for t, cols in schema_dict.items():
            schema_text += f"- Bảng {t}: {', '.join(cols)}\n"
            
        cursor.close()
        
        if len(schema_text) > 1500:
            table_names = list(schema_dict.keys())
            schema_text = "Cơ sở dữ liệu rất lớn. Dưới đây là danh sách tên các bảng:\n"
            schema_text += ", ".join(table_names)
            schema_text += "\n\n(GHI CHÚ: Mặc định tôi bị ẩn chi tiết cột để tiết kiệm bộ nhớ. Hãy dùng action 'READ' với câu lệnh 'SELECT * FROM user_tab_cols WHERE table_name = TÊN_BẢNG' để xem các cột trước khi tạo lệnh INSERT/UPDATE nếu bạn không nhớ rõ)."
            
        return schema_text.strip()
    except Exception as e:
        return ""

def run_sql_native(conn, sql_code, is_read=False):
    if conn is None:
        return False, "Database connection is not initialized."
    try:
        cursor = conn.cursor()
        if is_read:
            clean_sql = sql_code.strip()
            if clean_sql.endswith(';'):
                clean_sql = clean_sql[:-1]
            cursor.execute(clean_sql)
            
            rows = cursor.fetchall()
            if not rows:
                cursor.close()
                return True, "Truy vấn thành công nhưng không có dữ liệu (0 rows)."
            
            cols = [desc[0] for desc in cursor.description]
            output = [dict(zip(cols, row)) for row in rows]
            cursor.close()
            return True, json.dumps(output, ensure_ascii=False, indent=2, default=str)
        else:
            is_plsql_creation = re.search(r'\bCREATE\s+(OR\s+REPLACE\s+)?(PROCEDURE|FUNCTION|PACKAGE|TRIGGER)\b', sql_code, re.IGNORECASE)
            
            if re.search(r'\b(BEGIN|DECLARE)\b', sql_code, re.IGNORECASE):
                cursor.execute(sql_code)
            else:
                commands = sql_code.split(';')
                for cmd in commands:
                    cmd = cmd.strip()
                    if cmd:
                        cursor.execute(cmd)
            conn.commit()
            
            # Kiểm tra lỗi biên dịch PL/SQL
            if is_plsql_creation:
                cursor.execute("""
                    SELECT name, type, line, position, text 
                    FROM user_errors 
                    ORDER BY name, sequence
                """)
                errors = cursor.fetchall()
                if errors:
                    error_msg = "Lệnh thực thi thành công nhưng có lỗi biên dịch PL/SQL:\n"
                    for err in errors:
                        error_msg += f"- [{err[1]} {err[0]}] Dòng {err[2]}, Cột {err[3]}: {err[4]}\n"
                    cursor.close()
                    # Trả về False để AI hoặc UI biết có lỗi biên dịch
                    return False, error_msg

            cursor.close()
            return True, "Thực thi thành công!"
    except Exception as e:
        return False, str(e)

def export_table_to_sql(conn, table_name, deploy_folder=r"D:\APEX_Deploy_Scripts"):
    if conn is None:
        return False, "Database connection is not initialized."
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'SEGMENT_ATTRIBUTES', False); DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM, 'EMIT_SCHEMA', False); END;")
        
        cursor.execute(f"SELECT DBMS_METADATA.GET_DDL('TABLE', '{table_name}') FROM DUAL")
        row = cursor.fetchone()
        if not row:
            return False, f"Không tìm thấy bảng {table_name} ở DB Local."
        
        ddl_code = row[0].read() if hasattr(row[0], 'read') else str(row[0])
        clean_ddl = ddl_code.strip()
        if not clean_ddl.endswith(';'):
            clean_ddl += ";"
            
        cursor.execute(f"SELECT column_name FROM user_tab_cols WHERE table_name = '{table_name}' ORDER BY column_id")
        cols = [r[0] for r in cursor.fetchall()]
        
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        insert_sqls = []
        if rows:
            insert_sqls.append(f"-- ======================================================")
            insert_sqls.append(f"-- DỮ LIỆU CỦA BẢNG {table_name} ({len(rows)} BẢN GHI)")
            insert_sqls.append(f"-- ======================================================")
            
            cols_str = ", ".join(f'"{c}"' for c in cols)
            for r in rows:
                vals = []
                for val in r:
                    if val is None:
                        vals.append("NULL")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    elif isinstance(val, datetime.datetime):
                        vals.append(f"TO_DATE('{val.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')")
                    else:
                        val_esc = str(val).replace("'", "''")
                        vals.append(f"'{val_esc}'")
                
                vals_str = ", ".join(vals)
                insert_sqls.append(f"INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str});")
            insert_sqls.append("COMMIT;")
        
        data_script = "\n".join(insert_sqls)
        full_script = f"{clean_ddl}\n\n{data_script}\n"
        
        if not os.path.exists(deploy_folder):
            os.makedirs(deploy_folder)
            
        file_path = os.path.join(deploy_folder, f"{table_name.lower()}_deploy.sql")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_script)
            
        return True, {
            "file_path": file_path,
            "full_script": full_script,
            "filename": f"{table_name.lower()}_deploy.sql"
        }
    except Exception as e:
        return False, str(e)


def import_dataframe_to_table(conn, table_name, df):
    import pandas as pd
    if conn is None:
        return False, "Database connection is not initialized."
    try:
        cursor = conn.cursor()
        
        # Kiểm tra bảng có tồn tại không và lấy danh sách cột
        cursor.execute(f"SELECT column_name FROM user_tab_cols WHERE table_name = '{table_name.upper()}' ORDER BY column_id")
        db_cols = [r[0] for r in cursor.fetchall()]
        
        if not db_cols:
            return False, f"Bảng {table_name} không tồn tại trong Database."
            
        # Kiểm tra ánh xạ cột
        df.columns = [str(c).upper() for c in df.columns]
        
        valid_cols = [c for c in df.columns if c in db_cols]
        if not valid_cols:
            return False, "Không có cột nào trong File khớp với bảng trong Database."
            
        df_valid = df[valid_cols].copy()
        
        # Đảm bảo NaN được chuyển thành None cho oracledb
        df_valid = df_valid.astype(object).where(pd.notnull(df_valid), None)
        
        data_tuples = [tuple(x) for x in df_valid.to_numpy()]
        
        cols_str = ", ".join([f'"{c}"' for c in valid_cols])
        bind_vars = ", ".join([f":{i+1}" for i in range(len(valid_cols))])
        
        insert_sql = f"INSERT INTO {table_name.upper()} ({cols_str}) VALUES ({bind_vars})"
        
        cursor.executemany(insert_sql, data_tuples)
        conn.commit()
        
        inserted_rows = cursor.rowcount
        cursor.close()
        return True, f"Đã Import thành công {inserted_rows} dòng vào bảng {table_name.upper()}."
    except Exception as e:
        return False, f"Lỗi Import: {str(e)}"
