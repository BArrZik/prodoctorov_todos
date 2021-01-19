import os
import requests
import datetime
from pathlib import Path

# создание директории tasks
if not os.path.exists('./tasks'):
    os.makedirs('./tasks')


def get_json():
    response = {}
    todos_response = requests.get('https://json.medrating.org/todos')
    todos_response = todos_response.json()
    response['todos'] = todos_response
    users_response = requests.get('https://json.medrating.org/users')
    users_response = users_response.json()
    response['users'] = users_response
    return response


# создание новых отчетов и перезапись старых
def create_file(report, name):
    if os.path.isfile(f'./tasks/{name}.txt'):
        # получение даты старого отчета
        f_old = open(f'./tasks/{name}.txt', 'r')
        old = f_old.readlines()
        f_old.close()
        # берем из второй строки файла дату и время (два последних слова)
        old_date = old[1].split()
        old_date = old_date[-2:]
        # форматируем дату и время по заданию
        old_date = 'T'.join(old_date)

        p = Path(f'./tasks/{name}.txt')
        p.rename(f'./tasks/old_{name}_{old_date}.txt')

    # запись актуальных данных
    f = open(f'./tasks/{name}.txt', 'w')
    f.write(report)
    f.close()


# формирование строк заголовков задач в соответствии с заданной длиной
def task_titles(title):
    checked_title = ''
    if len(title) <= 48:
        checked_title += title + '\n'
    else:
        checked_title += title[0:48] + '...\n'
    return checked_title


# получение количества задач (общих/завершенных/незавершенных) и формирование списков заголовков задач
def get_tasks_status_and_titles(user_id, todos):
    tasks = {
        'all_tasks': 0,
        'completed_tasks': 0,
        'uncompleted_tasks': 0,
        'completed_titles': '',
        'uncompleted_titles': ''
    }

    for task in todos:
        if task.get('userId') == user_id:
            tasks['all_tasks'] += 1
            if task['completed']:
                tasks['completed_tasks'] += 1
                tasks['completed_titles'] += task_titles(task['title'])
            else:
                tasks['uncompleted_tasks'] += 1
                tasks['uncompleted_titles'] += task_titles(task['title'])
    return tasks


# составление отчета по пользователю и вызов функции создания файлов с отчетами
def make_report(user_entry, todos, report_time):
    if user_entry.get('name'):
        task_status = get_tasks_status_and_titles(user_entry['id'], todos)
        report = f'''Отчёт для {user_entry.get("company")["name"]}.
{user_entry["name"]} <{user_entry["email"]}> {report_time.strftime('%d.%m.%Y %H:%M')}
Всего задач: {task_status['all_tasks']}

Завершённые задачи: ({task_status['completed_tasks']}) 
{task_status['completed_titles']}
Оставшиеся задачи: ({task_status['uncompleted_tasks']})
{task_status['uncompleted_titles']}
'''
        create_file(report, user_entry['name'])


# вызов функции составления отчета для каждого пользователя
def main():
    now = datetime.datetime.now()
    try:
        response = get_json()
    except requests.exceptions.ConnectionError as e:
        print('Ошибка получения данных с сервера')
        raise e

    for user in response['users']:
        try:
            make_report(user_entry=user, todos=response['todos'], report_time=now)
        except Exception as e:
            print(f'Ошибка при обработке пользователя { user["id"] }')
            print(e)


if __name__ == '__main__':
    main()
