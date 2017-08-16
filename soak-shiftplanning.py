import random
from collections import defaultdict
import itertools
from argparse import ArgumentParser

random.seed(0)

parser = ArgumentParser()
parser.add_argument('teilnehmer')


penalties = {
    'same_meal': 2,
    'known_partner': 10,
    'day_before': 25,
    'same_day': 100,
}


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


def get_available_workers(shifts, workers, assigned_workers, meal, partners):
    available_workers = workers - assigned_workers
    available_workers = filter(lambda w: has_leisure_time(shifts, w), available_workers)
    available_workers = list(filter(
        lambda w: has_no_meal(shifts, w, meal), available_workers
    ))

    for worker in available_workers.copy():
        if any(p in partners for p in shifts[worker]['partners']):
            available_workers.remove(worker)

    return available_workers


def pick_worker(available_workers):
    return random.choice(list(available_workers))


def pick_workers(shifts, workers, meal):
    assigned_workers = set()
    partners = set()

    for i in range(3):
        available_workers = get_available_workers(shifts, workers, assigned_workers, meal, partners)
        worker = pick_worker(available_workers)
        assigned_workers.add(worker)
        partners.update(shifts[worker]['partners'])

    for w1, w2 in itertools.combinations(assigned_workers, 2):
        add_partners(shifts, w1, w2)

    for worker in assigned_workers:
        decrease_leisure_time(shifts, worker)
        increase_assignment(shifts, worker, meal)

    return assigned_workers


def create_week_plan(workers):
    shifts = init_worker_bookkeeping()
    weekplan = defaultdict(dict)

    assigned_workers = set()

    for day in days:
        if day is 'sunday_departure':
            meals = ['breakfast']
        else:
            meals = ['breakfast', 'lunch', 'dinner']

        assigned_workers_day = set()

        for meal in meals:
            assigned_workers_meal = pick_workers(shifts, workers, meal)
            assigned_workers_day.update(assigned_workers_meal)

            weekplan[day][meal] = list(assigned_workers_meal)

        for worker in assigned_workers:
            increase_leisure_time(shifts, worker)

        assigned_workers = assigned_workers_day

    return weekplan, shifts


def main():
    args = parser.parse_args()

    with open(args.teilnehmer) as f:
        workers = set(map(str.strip, f.read().splitlines()))

    print('Starting iteration')

    very_lucky_people = True
    counter = 0
    while very_lucky_people:
        counter += 1

        print(f'Iteration {counter}')

        try:
            weekplan, shifts = create_week_plan(workers)
        except IndexError as e:
            print(e)
            continue

        shift_counts = {
            w: shifts[w]['breakfast'] + shifts[w]['lunch'] + shifts[w]['dinner']
            for w in workers
        }

        lucky_people = sum(s < 3 for s in shift_counts.values())
        print('  Lucky people:', lucky_people)

        very_lucky_people = sum(s < 2 for s in shift_counts.values())
        print('  Very lucky people:', very_lucky_people)

    print('\n\n')
    for day, meals in weekplan.items():
        print(f'{f"  {day}  ":#^30}')
        for meal, assigned_workers in meals.items():
            print('  {:15}: {}, {}, {}'.format(meal, *list(assigned_workers)))

        print()
    print()

    for w, c in sorted(shift_counts.items(), key=lambda w: w[1]):
        print(f'{w:25} {c}')


if __name__ == '__main__':
    main()
