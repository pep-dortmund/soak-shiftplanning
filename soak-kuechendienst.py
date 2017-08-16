import random
from collections import defaultdict

days = [
    'sunday_arrival',
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday_departure',
]


def init_worker_bookkeeping():
    return defaultdict(lambda: {
        'breakfast': 0,
        'lunch': 0,
        'dinner': 0,
        'partners': [],
        'leisure_time': 1,
    })


def increase_leisure_time(shifts, worker):
    shifts[worker]['leisure_time'] = 1


def decrease_leisure_time(shifts, worker):
    shifts[worker]['leisure_time'] = 0


def increase_assignment(shifts, worker, assignement):
    shifts[worker][assignement] += 1


def add_partners(shifts, one, two):
    shifts[one]['partners'].append(two)
    shifts[two]['partners'].append(one)


def has_leisure_time(shifts, worker):
    return shifts[worker]['leisure_time'] is 1


def has_no_meal(shifts, worker, meal):
    return shifts[worker][meal] is 0


def get_available_workers(shifts, assigned_workers, meal, partners):
    available_workers = workers - assigned_workers
    available_workers = filter(lambda w: has_leisure_time(shifts, w), available_workers)
    available_workers = list(filter(
        lambda w: has_no_meal(shifts, w, meal), available_workers
    ))

    for partner in partners:
        for worker in workers:
            if partner in shifts[worker]['partners']:
                if worker in available_workers:
                    available_workers.remove(worker)

    # print 'AW after checking partners', len(available_workers)

    return available_workers


def pick_worker(available_workers):
    return random.choice(list(available_workers))


def pick_workers(shifts, meal):
    assigned_workers = set([])
    partners = set([])

    available_workers = get_available_workers(shifts, assigned_workers, meal, partners)
    if len(available_workers) < 3:
        raise ValueError(
            'Not enough available workers: {}'.format(len(available_workers))
        )

    one = pick_worker(available_workers)
    assigned_workers.add(one)
    partners.update(shifts[one]['partners'])

    available_workers = get_available_workers(shifts, assigned_workers, meal, partners)
    if len(available_workers) < 2:
        raise ValueError(
            'Not enough available workers: {}'.format(len(available_workers))
        )

    two = pick_worker(available_workers)
    assigned_workers.add(two)
    partners.update(shifts[two]['partners'])

    available_workers = get_available_workers(shifts, assigned_workers, meal, partners)
    if len(available_workers) < 1:
        raise ValueError(
            'Not enough available workers: {}'.format(len(available_workers))
        )

    three = pick_worker(available_workers)
    assigned_workers.add(three)

    add_partners(shifts, one, two)
    add_partners(shifts, one, three)
    add_partners(shifts, two, three)

    for worker in assigned_workers:
        decrease_leisure_time(shifts, worker)
        increase_assignment(shifts, worker, meal)

    return assigned_workers


def create_week_plan(workers):
        shifts = init_worker_bookkeeping()
        assigned_workers = set()

        for day in days:
            if day is 'sunday_departure':
                meals = ['breakfast']
            else:
                meals = ['breakfast', 'lunch', 'dinner']

            assigned_workers_daylist = set()

            for meal in meals:
                assigned_workers_meallist = pick_workers(shifts, meal)
                assigned_workers_daylist.update(assigned_workers_meallist)

                print('{0:20} {1:15} {2}'.format(day, meal, assigned_workers_meallist))

            for worker in assigned_workers:
                increase_leisure_time(shifts, worker)

            assigned_workers = assigned_workers_daylist

        return shifts


if __name__ == '__main__':
    with open('teilnehmer.txt') as f:
        workers = set(map(str.strip, f.read().splitlines()))

    print('Starting iteration')

    very_lucky_people = True
    while very_lucky_people:

        try:
            shifts = create_week_plan(workers)
        except ValueError:
            print('Not successfull')
            continue

        very_lucky_people = False
        for worker in workers:
            if shifts[worker]['breakfast'] + shifts[worker]['lunch'] + shifts[worker]['dinner'] == 1 or shifts[worker]['breakfast'] + shifts[worker]['lunch'] + shifts[worker]['dinner'] == 0:
                very_lucky_people = True

    print('\nLucky:')
    for worker in workers:
        if shifts[worker]['breakfast'] + shifts[worker]['lunch'] + shifts[worker]['dinner'] == 2:
            print(worker)

    print('\nVery Lucky:')
    for worker in workers:
        if shifts[worker]['breakfast'] + shifts[worker]['lunch'] + shifts[worker]['dinner'] == 1:
            print(worker)

    print('\nVery Very Lucky (if somebody turns out to be here you should definetly think about replacing somebody unlucky with him):')
    for worker in workers:
        if shifts[worker]['breakfast'] + shifts[worker]['lunch'] + shifts[worker]['dinner'] == 0:
            print(worker)
