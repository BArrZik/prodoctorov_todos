import os
import requests
import datetime


# создание директории tasks
if not os.path.exists('./tasks'):
    os.makedirs('./tasks')


# получение списка задач
todos_response = requests.get('https://json.medrating.org/todos')
todos_response = todos_response.json()


# получение списка пользователей
users_response = requests.get('https://json.medrating.org/users')
users_response = users_response.json()


# получение актуального времени составления отчета
now = datetime.datetime.now()


# создание новых отчетов и перезапись старых
def create_file(report, name):
    # создание отчетов со старыми данными и перезапись актуальных отчетов
    if os.path.isfile(f'./tasks/{name}.txt'):
        # получение даты старого отчета
        f_old = open(f'./tasks/{name}.txt', 'r')
        old = f_old.readlines()
        f_old.close()
        old_date = old[1].split()
        old_date = old_date[-2:]
        old_date = 'T'.join(old_date)

        # получение текста старого отчета
        f_old = open(f'./tasks/{name}.txt', 'r')
        old_text = f_old.read()
        f_old.close()

        # запись актуального отчета в актуальный файл
        f = open(f'./tasks/{name}.txt', 'w')
        f.write(report)
        f.close()

        # запись старого отчета в файл с требуемым названием
        f_new_old = open(f'./tasks/old_{ name }_{ old_date }.txt', 'w')
        f_new_old.write(old_text)
        f_new_old.close()

    # создание актуального отчета, если еще не существует
    else:
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
    all_tasks = 0
    completed_tasks = 0
    uncompleted_tasks = 0
    completed_titles = ''
    uncompleted_titles = ''
    for task in todos:
        if task.get('userId') == user_id:
            all_tasks += 1
            if task['completed']:
                completed_tasks += 1
                completed_titles += task_titles(task['title'])
            else:
                uncompleted_tasks += 1
                uncompleted_titles += task_titles(task['title'])
    return all_tasks, completed_tasks, uncompleted_tasks, completed_titles, uncompleted_titles


# составление отчета по пользователю и вызов функции создания файлов с отчетами
def make_report(current_user, todos):
    if current_user.get('name'):
        task_status = get_tasks_status_and_titles(current_user['id'], todos)
        report = f'Отчёт для { current_user.get("company")["name"] }. \n'
        report += f'{ current_user["name"]} <{ current_user["email"]}> ' + now.strftime('%d.%m.%Y %H:%M') + '\n'
        report += f'Всего задач: { task_status[0] } \n \n'
        report += f'Завершённые задачи: ({ task_status[1] }) \n'
        report += task_status[3] + '\n'
        report += f'Оставшиеся задачи: ({ task_status[2] }) \n'
        report += task_status[4] + '\n'
        create_file(report, current_user['name'])


# вызов функции составления отчета для каждого пользователя
for user in users_response:
    make_report(user, todos_response)
