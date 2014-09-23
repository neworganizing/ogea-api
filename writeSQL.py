import psycopg2
import psycopg2.extras
import datetime
from config import DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD

con = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USERNAME,
    password=DB_PASSWORD
)

cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)


def process_query(data):
    keys = [c[0] for c in cur.description]
    end_data = []
    for row in data:
        dict_row = dict.fromkeys(keys)
        for r, k in zip(row, keys):
            if k == 'a_id':
                cur.execute("""
                    select ogea_citation.url
                        from ogea_answer
                        join ogea_answer_citations
                            on ogea_answer.id =
                                ogea_answer_citations.answer_id
                        join ogea_citation
                            on ogea_citation.id =
                                ogea_answer_citations.citation_id
                        where ogea_answer.id = (%s);
                """, (r,))
                cites = cur.fetchall()
                count = 1
                for c in cites:
                    dict_row["cite" + str(count)] = c[0]
                    count += 1
                dict_row.pop("a_id", None)
            else:
                dict_row[k] = r
        try:
            dict_row['date_aq'] = '{}-{}-{}'.format(
                dict_row['date_aq'].year,
                dict_row['date_aq'].month,
                dict_row['date_aq'].day
            )
        except:
            pass
        end_data.append(dict_row)
    return end_data


def state_question_id_sql(state, q_id):
    cur.execute("""
        select ogea_state.name as state, ogea_answer.text as answer,
               ogea_answer.id as a_id, ogea_answer.confirmed_on as conf_date,
               ogea_answer.created as date_aq
            from ogea_state
            inner join ogea_answer
                on ogea_state.id = ogea_answer.state_id
            inner join ogea_question
                on ogea_answer.question_id = ogea_question.id
            where ogea_state.abbrv = (%s) and ogea_question.id = (%s);
        """, (state, q_id))
    return process_query(cur.fetchall())


def state_question_sql(state, ques):
    cur.execute("""
        select ogea_state.name as state, ogea_answer.text as answer,
               ogea_answer.id as a_id, ogea_answer.confirmed_on as conf_date,
               ogea_answer.created as date_aq
            from ogea_state
            inner join ogea_answer
                on ogea_state.id = ogea_answer.state_id
            inner join ogea_question
                on ogea_answer.question_id = ogea_question.id
            where ogea_state.abbrv = (%s) and ogea_question.text = (%s);
        """, (state, ques))
    return process_query(cur.fetchall())


# THIS COMBINES FIELDS
def questions_sql():
    query = """
        select ogea_question.text as question_text, ogea_question.id,
               ogea_subtopic.name as subtopic, ogea_topic.name as topic
            from ogea_question
            inner join ogea_subtopic
                on ogea_question.subtopic_id=ogea_subtopic.id
            inner join ogea_topic
                on ogea_subtopic.topic_id=ogea_topic.id;
    """
    cur.execute(query)
    return process_query(cur.fetchall())


def question_name_sql(ques):
    query = """
        select ogea_state.name as state, ogea_answer.text as answer,
               ogea_answer.id as a_id, ogea_answer.confirmed_on as conf_date,
               ogea_answer.created as date_aq
            from ogea_state
            inner join ogea_answer
                on ogea_state.id = ogea_answer.state_id
            inner join ogea_question
                on ogea_answer.question_id = ogea_question.id
        where ogea_question.text = '{0}';
    """.format(ques)
    cur.execute(query)
    return process_query(cur.fetchall())


def question_id_sql(q_id):
    cur.execute("""
        select ogea_state.name as state, ogea_answer.text as answer,
               ogea_answer.id as a_id, ogea_answer.confirmed_on as conf_date,
               ogea_answer.created as date_aq
            from ogea_state
            inner join ogea_answer
                on ogea_state.id = ogea_answer.state_id
            inner join ogea_question
                on ogea_answer.question_id = ogea_question.id
        where ogea_question.id = (%s);
    """, (q_id,))
    return process_query(cur.fetchall())


def state_sql(state):
    cur.execute("""
        select ogea_state.name as state, ogea_topic.name as topic,
               ogea_subtopic.name as subtopic, ogea_question.text as question,
               ogea_answer.text as answer, ogea_answer.id as a_id,
               ogea_answer.confirmed_on as conf_date,
               ogea_answer.created as date_aq
            from ogea_state
            inner join ogea_answer
                on ogea_state.id = ogea_answer.state_id
            inner join ogea_question
                on ogea_answer.question_id = ogea_question.id
            inner join ogea_subtopic
                on ogea_question.subtopic_id = ogea_subtopic.id
            inner join ogea_topic
                on ogea_subtopic.topic_id = ogea_topic.id
        where ogea_state.abbrv = (%s);
    """, (state,))
    return process_query(cur.fetchall())


def get_api_token(username):
    cur.execute("""
        select *
            from ogea_apikey
        where username='{0}'
        limit 1;
    """.format(username))
    result = cur.fetchone()

    # is it stale?
    if result:
        if result[2] and result[2] < datetime.date.today():
            # Remove old token
            cur.execute("""
                delete
                    from ogea_apikey
                where username='{0}'
            """.format(username))
            return None
        else:
            return result[1]  # [id, token, expiration, username]

    return None


def insert_api_token(username, token, date):
    cur.execute("""
        insert
            into ogea_apikey(username, key, expiration)
        values ('{0}', '{1}', '{2}');
    """.format(
        username, token, date)
    )
    con.commit()
    # return process_query(cur.fetchall())


def get_api_token_expiration(token):
    if token:
        cur.execute("""
            select expiration
                from ogea_apikey
            where key='{0}'
        """.format(token))
        return process_query(cur.fetchall())

    return None


def dump_sql():
    cur.execute("""
        select ogea_state.name as state, ogea_topic.name as topic,
               ogea_subtopic.name as subtopic, ogea_question.text as question,
               ogea_question.id as ques_id, ogea_answer.id as a_id,
               ogea_answer.text as answer,
               ogea_answer.confirmed_on as conf_date,
               ogea_answer.created as date_aq
            from ogea_state
            inner join ogea_answer
                on ogea_state.id = ogea_answer.state_id
            inner join ogea_question
                on ogea_answer.question_id = ogea_question.id
            inner join ogea_subtopic
                on ogea_question.subtopic_id = ogea_subtopic.id
            inner join ogea_topic
                on ogea_subtopic.topic_id = ogea_topic.id;
        """)
    return process_query(cur.fetchall())
