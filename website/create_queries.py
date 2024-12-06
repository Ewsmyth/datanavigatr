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
                            chats.id || '<reporterChatID>' AS CONTENT_ID,
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

def create_vendify_query():
    try:
        with current_app.app_context():
            search_for_query = IngestQuery.query.filter_by(name='Vendify Query').first()

            if not search_for_query:
                print("No Vendify ingest query, attempting to create Vendify Query.")

                query_code = """
                    SELECT
                        user.id || '<vendifyID>' AS TX_USER_ID,
                        NULL AS RX_USER_ID,
                        user.username || '<vendifyUsrnm>' AS TX_ASSOC_USRNM,
                        'VENDIFY_POST' AS EVENT,
                        NULL AS TX_ASSOC_EMAIL,
                        NULL AS TX_ACCT_PASSWD,
                        NULL AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        NULL AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        post.id || '<vendifyObj>' AS CONTENT_ID,
                        GROUP_CONCAT(media.media_url || ', ' || post.cover_photo_url, ', ') AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        post.title AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', post.created_at) AS UP_TIME,
                        post.created_at AS INITIAL_TIME
                    FROM post
                    JOIN user ON post.author_id = user.id
                    LEFT JOIN media ON post.id = media.post_id
                    GROUP BY post.id

                    UNION ALL

                    SELECT
                        order_table.purchaser_id || '<vendifyID>' AS TX_USER_ID,
                        order_item.vendor_id || '<vendifyID>' AS RX_USER_ID,
                        (SELECT username FROM user WHERE id = order_table.purchaser_id) || '<vendifyUsrnm>' AS TX_ASSOC_USRNM,
                        'ORDER' AS EVENT,
                        NULL AS TX_ASSOC_EMAIL,
                        NULL AS TX_ACCT_PASSWD,
                        NULL AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        NULL AS TX_ACCT_STATUS,
                        order_table.phone_number AS TX_ASSOC_PHONE,
                        order_table.shipping_address || ' ' || order_table.shipping_city || ' ' || order_table.shipping_state || ' ' || order_table.shipping_country || ' ' || CAST(order_table.shipping_zipcode AS TEXT) AS LOCATION,
                        order_table.card_number AS FINANCE_ID,
                        order_item.post_id || '<vendifyObj>' AS CONTENT_ID,
                        NULL AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        order_table.order_status AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', order_table.updated_at) AS UP_TIME,
                        order_table.created_at AS INITIAL_TIME
                    FROM "order" AS order_table
                    JOIN order_item ON order_table.id = order_item.order_id
                    GROUP BY order_table.id, order_item.post_id, order_item.vendor_id

                    UNION ALL

                    SELECT
                        user.id || '<vendifyID>' AS TX_USER_ID,
                        NULL AS RX_USER_ID,
                        user.username || '<vendifyUsrnm>' AS TX_ASSOC_USRNM,
                        'USER_ACCT' AS EVENT,
                        NULL AS TX_ASSOC_EMAIL,
                        user.password AS TX_ACCT_PASSWD,
                        user.authority AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        user.is_active AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        NULL AS CONTENT_ID,
                        NULL AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        NULL AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', user.updated_at) AS UP_TIME,
                        user.created_at AS INITIAL_TIME
                    FROM user
                    ORDER BY up_time DESC;
                    """

                sql_query_dir = current_app.config.get('SQL_QUERY_DIR')
                if not sql_query_dir:
                    sql_query_dir = os.path.join(os.getcwd(), 'sql_queries')
                    os.makedirs(sql_query_dir, exist_ok=True)

                query_filename = "vendify_query.txt"
                query_filepath = os.path.join(sql_query_dir, query_filename)

                with open(query_filepath, 'w') as f:
                    f.write(query_code)

                build_vendify_query = IngestQuery(
                    name='Vendify Query',
                    sql_query=query_filepath,
                    created_by='1',
                    edited_by='1'
                )
                db.session.add(build_vendify_query)
                db.session.commit()
                print("Vendify Query successfully created.")
    except Exception as e:
        print(f"Error creating Vendify Query: {e}")

def create_interactify_query():
    try:
        with current_app.app_context():
            search_for_query = IngestQuery.query.filter_by(name='Interactify Query').first()

            if not search_for_query:
                print("No Interactify ingest query, attempting to create Interactify Query.")

                query_code = """
                    SELECT
                        user.id || '<interactifyID>' AS TX_USER_ID,
                        NULL AS RX_USER_ID,
                        user.username || '<interactifyUsrnm>' AS TX_ASSOC_USRNM,
                        'POST' AS EVENT,
                        NULL AS TX_ASSOC_EMAIL,
                        NULL AS TX_ACCT_PASSWD,
                        NULL AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        NULL AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        post.id || '<interactifyObj>' AS CONTENT_ID,
                        GROUP_CONCAT(media.media_url, ', ') AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        post.content AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', post.updated_at) AS UP_TIME,
                        NULL AS INITIAL_TIME
                    FROM post
                    JOIN user ON post.author_id = user.id
                    LEFT JOIN media ON post.id = media.post_id
                    GROUP BY post.id

                    UNION ALL

                    SELECT
                        likes.liked_by || '<interactifyID>' AS TX_USER_ID,
                        post.author_id || '<interactifyID>' AS RX_USER_ID,
                        user_like.username || '<interactifyUsrnm>' AS TX_ASSOC_USRNM,
                        'LIKE' AS EVENT,
                        NULL AS TX_ASSOC_EMAIL,
                        NULL AS TX_ACCT_PASSWD,
                        NULL AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        NULL AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        likes.liked_post || '<interactifyObj>' AS CONTENT_ID,
                        NULL AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        NULL AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', likes.updated_at) AS UP_TIME,
                        NULL AS INITIAL_TIME
                    FROM likes
                    JOIN post ON likes.liked_post = post.id
                    JOIN user AS user_like ON likes.liked_by = user_like.id
                    JOIN user AS user_post ON post.author_id = user_post.id

                    UNION ALL

                    SELECT
                        comment.user_id || '<interactifyID>' AS TX_USER_ID,
                        post.author_id || '<interactifyID>' AS RX_USER_ID,
                        user_comment.username || '<interactifyUsrnm>' AS TX_ASSOC_USRNM,
                        'COMMENT' AS EVENT,
                        users.email AS TX_ASSOC_EMAIL,
                        users.password AS TX_ACCT_PASSWD,
                        NULL AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        NULL AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        comment.post_id || '<interactifyObj>' AS CONTENT_ID,
                        GROUP_CONCAT(media.media_url, ', ') AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        comment.content AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', comment.updated_at) AS UP_TIME,
                        NULL AS INITIAL_TIME
                    FROM comment
                    JOIN post ON comment.post_id = post.id
                    JOIN user AS user_comment ON comment.user_id = user_comment.id
                    JOIN user AS user_post ON post.author_id = user_post.id
                    LEFT JOIN media ON post.id = media.post_id
                    GROUP BY comment.id

                    UNION ALL

                    SELECT
                        follower.follower_id || '<interactifyID>' AS TX_USER_ID,
                        follower.following_id || '<interactifyID>' AS RX_USER_ID,
                        user_follower.username || '<interactifyUsrnm>' AS TX_ASSOC_USRNM,
                        'FOLLOW' AS EVENT,
                        NULL AS TX_ASSOC_EMAIL,
                        NULL AS TX_ACCT_PASSWD,
                        NULL AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        NULL AS TX_ASSOC_FNAME,
                        NULL AS TX_ASSOC_LNAME,
                        NULL AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        NULL AS CONTENT_ID,
                        NULL AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        NULL AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', follower.created_at) AS UP_TIME,
                        NULL AS INITIAL_TIME
                    FROM follower
                    JOIN user AS user_follower ON follower.follower_id = user_follower.id
                    JOIN user AS user_following ON follower.following_id = user_following.id

                    UNION ALL

                    SELECT
                        user.id || '<interactifyID>' AS TX_USER_ID,
                        NULL AS RX_USER_ID,
                        user.username || '<interactifyUsrnm>' AS TX_ASSOC_USRNM,
                        'USER_ACCT' AS EVENT,
                        user.email AS TX_ASSOC_EMAIL,
                        user.password AS TX_ACCT_PASSWD,
                        user.authority AS TX_ACCT_AUTH,
                        NULL AS TX_CTL_BY,
                        NULL AS TX_ASSOC_TEAM,
                        user.first_name AS TX_ASSOC_FNAME,
                        user.last_name AS TX_ASSOC_LNAME,
                        user.acct_stat AS TX_ACCT_STATUS,
                        NULL AS TX_ASSOC_PHONE,
                        NULL AS LOCATION,
                        NULL AS FINANCE_ID,
                        NULL AS CONTENT_ID,
                        user.profile_picture AS MEDIA,
                        NULL AS GROUP_PARTICIPANTS,
                        NULL AS GROUP_CHAT_NAME,
                        user.bio AS CONTENT,
                        strftime('%Y-%m-%d %H:%M:%S', user.updated_at) AS UP_TIME,
                        user.created_at AS INITIAL_TIME
                    FROM user
                    ORDER BY up_time DESC;
                    """

                sql_query_dir = current_app.config.get('SQL_QUERY_DIR')
                if not sql_query_dir:
                    sql_query_dir = os.path.join(os.getcwd(), 'sql_queries')
                    os.makedirs(sql_query_dir, exist_ok=True)

                query_filename = "interactify_query.txt"
                query_filepath = os.path.join(sql_query_dir, query_filename)

                with open(query_filepath, 'w') as f:
                    f.write(query_code)

                build_interactify_query = IngestQuery(
                    name='Interactify Query',
                    sql_query=query_filepath,
                    created_by='1',
                    edited_by='1'
                )
                db.session.add(build_interactify_query)
                db.session.commit()
                print("Interactify Query successfully created.")
    except Exception as e:
        print(f"Error creating Interactify Query: {e}")