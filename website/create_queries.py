from flask import current_app
from .models import db, IngestQuery
import os

def create_reporter_query():
    try:
        with current_app.app_context():
            search_for_query = IngestQuery.query.filter_by(name='Reporter Query').first()

            if not search_for_query:
                print("No Reporter ingest query, attempting to create Reporter Query.")

                query_code = """
                        SELECT
                            contacts.user_id || '<reporterID>' AS TX_USER_ID,
                            contacts.contact_id || '<reporterID>' AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'USER_CONTACT' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            NULL AS CONTENT_ID,
                            NULL AS MEDIA,
                            NULL AS GROUP_PARTICIPANTS,
                            NULL AS GROUP_CHAT_NAME,
                            NULL AS CONTENT,
                            contacts.added_at AS UP_TIME,
                            NULL AS INITIAL_TIME
                        FROM contacts
                        JOIN users ON contacts.user_id = users.id

                        UNION ALL

                        SELECT
                            users.id || '<reporterID>' AS TX_USER_ID,
                            NULL AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'USER_ACCT' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            NULL AS CONTENT_ID,
                            NULL AS MEDIA,
                            NULL AS GROUP_PARTICIPANTS,
                            NULL AS GROUP_CHAT_NAME,
                            NULL AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', users.updated_at) AS UP_TIME,
                            strftime('%Y-%m-%d %H:%M:%S', users.created_at) AS INITIAL_TIME
                        FROM users

                        UNION ALL

                        SELECT
                            group_chat_details.created_by || '<reporterID>' AS TX_USER_ID,
                            NULL AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'NEW_CHAT' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            chats.id || '<reporterChatID>' CONTENT_ID,
                            NULL AS MEDIA,
                            GROUP_CONCAT(chat_participants.user_id || '<reporterID>', ', ') AS GROUP_PARTICIPANTS,
                            group_chat_details.group_name AS GROUP_CHAT_NAME,
                            NULL AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', group_chat_details.updated_at) AS UP_TIME,
                            strftime('%Y-%m-%d %H:%M:%S', chats.created_at) AS INITIAL_TIME
                        FROM chats
                        JOIN chat_participants ON chat_participants.chat_id = chats.id
                        LEFT JOIN group_chat_details ON group_chat_details.chat_id = chats.id
                        LEFT JOIN users ON group_chat_details.created_by = users.id
                        GROUP BY chats.id

                        UNION ALL

                        SELECT
                            users.id || '<reporterID>' AS TX_USER_ID,
                            GROUP_CONCAT(
                                CASE
                                    WHEN chat_participants.user_id != users.id THEN chat_participants.user_id || '<reporterID>'
                                    ELSE NULL
                                END, ', ') AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'MESSAGE' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            chats.id || '<reporterChatID>' AS CONTENT_ID,
                            NULL AS MEDIA,
                            GROUP_CONCAT(chat_participants.user_id || '<reporterID>', ', ') AS GROUP_PARTICIPANTS,
                            group_chat_details.group_name AS GROUP_CHAT_NAME,
                            messages.content AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', messages.timestamp) AS UP_TIME,
                            NULL AS INITIAL_TIME
                        FROM messages
                        JOIN users ON messages.sender_id = users.id
                        LEFT JOIN chats ON messages.chat_id = chats.id
                        LEFT JOIN chat_participants ON chats.id = chat_participants.chat_id
                        LEFT JOIN group_chat_details ON chats.id = group_chat_details.chat_id
                        GROUP BY messages.id, users.id

                        UNION ALL

                        SELECT
                            reports.author_id || '<reporterID>' AS TX_USER_ID,
                            NULL AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'SPOTREP' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            NULL AS CONTENT_ID,
                            NULL AS MEDIA,
                            NULL AS GROUP_PARTICIPANTS,
                            NULL AS GROUP_CHAT_NAME,
                            GROUP_CONCAT(
                                reports.report_type || ': ' ||
                                'Size: ' || reports.size || ', ' ||
                                'Activity: ' || reports.activity || ', ' ||
                                'Location: ' || reports.location || ', ' ||
                                'Unit: ' || reports.unit || ', ' ||
                                'Time: ' || reports.report_time || ', ' ||
                                'Equipment: ' || reports.equipment
                            ) AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', reports.created_at) AS UP_TIME,
                            NULL AS INITIAL_TIME
                        FROM reports
                        JOIN users ON reports.author_id = users.id
                        WHERE reports.report_type = 'SPOTREP'
                        GROUP BY reports.author_id, users.username, users.email

                        UNION ALL

                        SELECT
                            reports.author_id || '<reporterID>' AS TX_USER_ID,
                            NULL AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'POSREP' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            NULL AS CONTENT_ID,
                            NULL AS MEDIA,
                            NULL AS GROUP_PARTICIPANTS,
                            NULL AS GROUP_CHAT_NAME,
                            GROUP_CONCAT(
                                reports.report_type || ': ' ||
                                'Team: ' || reports.team || ', ' ||
                                'Location: ' || reports.location || ', ' ||
                                'Time: ' || reports.report_time
                            ) AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', reports.created_at) AS UP_TIME,
                            NULL AS INITIAL_TIME
                        FROM reports
                        JOIN users ON reports.author_id = users.id
                        WHERE reports.report_type = 'POSREP'
                        GROUP BY reports.author_id, users.username, users.email

                        UNION ALL

                        SELECT
                            reports.author_id || '<reporterID>' AS TX_USER_ID,
                            NULL AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'MISREP' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            NULL AS CONTENT_ID,
                            NULL AS MEDIA,
                            NULL AS GROUP_PARTICIPANTS,
                            NULL AS GROUP_CHAT_NAME,
                            GROUP_CONCAT(
                                reports.report_type || ': ' ||
                                'Mission Name: ' || reports.mission_name || ', ' ||
                                'Result: ' || reports.result || ', ' ||
                                'Mission Details: ' || reports.mission_details
                            ) AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', reports.created_at) AS UP_TIME,
                            NULL AS INITIAL_TIME
                        FROM reports
                        JOIN users ON reports.author_id = users.id
                        WHERE reports.report_type = 'MISREP'
                        GROUP BY reports.author_id, users.username, users.email

                        UNION ALL

                        SELECT
                            reports.author_id || '<reporterID>' AS TX_USER_ID,
                            NULL AS RX_USER_ID,
                            users.username || '<reporterUsrnm>' AS TX_ASSOC_USRNM,
                            'DFREP' AS EVENT,
                            users.email AS TX_ASSOC_EMAIL,
                            users.password AS TX_ACCT_PASSWD,
                            users.auth AS TX_ACCT_AUTH,
                            users.manager_id AS TX_CTL_BY,
                            users.team AS TX_ASSOC_TEAM,
                            users.firstname AS TX_ASSOC_FNAME,
                            users.lastname AS TX_ASSOC_LNAME,
                            users.is_active AS TX_ACCT_STATUS,
                            NULL AS TX_ASSOC_PHONE,
                            NULL AS LOCATION,
                            NULL AS FINANCE_ID,
                            NULL AS CONTENT_ID,
                            NULL AS MEDIA,
                            NULL AS GROUP_PARTICIPANTS,
                            NULL AS GROUP_CHAT_NAME,
                            GROUP_CONCAT(
                                reports.report_type || ': ' ||
                                'Time: ' || reports.report_time || ', ' ||
                                'Location: ' || reports.location || ', ' ||
                                'Azimuth: ' || reports.azimuth || ', ' ||
                                'Frequency: ' || reports.frequency || ', ' ||
                                'RSSI: ' || reports.rssi || ', ' ||
                                'Modulation: ' || reports.modulation || ', ' ||
                                'Technology: ' || reports.technology || ', ' ||
                                'Protocol: ' || reports.protocol
                            ) AS CONTENT,
                            strftime('%Y-%m-%d %H:%M:%S', reports.created_at) AS UP_TIME,
                            NULL AS INITIAL_TIME
                        FROM reports
                        JOIN users ON reports.author_id = users.id
                        WHERE reports.report_type = 'DFREP'
                        GROUP BY reports.author_id, users.username, users.email

                        ORDER BY UP_TIME DESC;
                    """

                sql_query_dir = current_app.config.get('SQL_QUERY_DIR')
                if not sql_query_dir:
                    sql_query_dir = os.path.join(os.getcwd(), 'sql_queries')
                    os.makedirs(sql_query_dir, exist_ok=True)

                query_filename = "reporter_query.txt"
                query_filepath = os.path.join(sql_query_dir, query_filename)

                with open(query_filepath, 'w') as f:
                    f.write(query_code)

                build_reporter_query = IngestQuery(
                    name='Reporter Query',
                    sql_query=query_filepath,
                    created_by='1',
                    edited_by='1'
                )
                db.session.add(build_reporter_query)
                db.session.commit()
                print("Reporter Query successfully created.")
    except Exception as e:
        print(f"Error creating Reporter Query: {e}")
