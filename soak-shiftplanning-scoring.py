import random
from collections import defaultdict
import itertools
from argparse import ArgumentParser

random.seed(0)

parser = ArgumentParser()
parser.add_argument('teilnehmer')

num_workers = 3
max_allowed_score = 400

meals = defaultdict(lambda: ['breakfast', 'lunch', 'dinner'])
meals['sunday_departure'] = ['breakfast']

penalties = {
    'same_meal': 5,
    'day_before': 23,
    'known_partner': 47,
    'total_shifts': 100,
    'same_day': 200,
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
        'total_score': 0,
        'breakfast': 0,
        'lunch': 0,
        'dinner': 0,
        'partners': [],
        'leisure_time': 1,
    })


def increase_assignment(shifts, worker, assignement):
    shifts[worker][assignement] += 1


def add_partners(shifts, one, two):
    shifts[one]['partners'].append(two)
    shifts[two]['partners'].append(one)


def pick_worker(available_workers):
    return random.choice(list(available_workers))


def pick_workers(shifts, workers, meal, weekplan):
    assigned_workers = set()

    for i in range(num_workers):
        scores = score_workers(
            shifts, workers, assigned_workers, meal, weekplan
        )

        min_score = min(scores.values())

        workers_with_min_score = [
            worker for worker, score in scores.items()
            if score == min_score
        ]
        worker = pick_worker(workers_with_min_score)
        assigned_workers.add(worker)
        shifts[worker]['total_score'] += min_score

    for w1, w2 in itertools.combinations(assigned_workers, 2):
        add_partners(shifts, w1, w2)

    for worker in assigned_workers:
        increase_assignment(shifts, worker, meal)

    return assigned_workers


def score_workers(shifts, workers, assigned_workers, meal, weekplan):
    scores = defaultdict(int)

    for worker in workers - assigned_workers:
        n_same_day = sum(worker in m for m in weekplan[-1].values())
        scores[worker] += n_same_day * penalties['same_day']

        if len(weekplan) > 1:
            n_day_before = sum(worker in m for m in weekplan[-2].values())
            scores[worker] += n_day_before * penalties['day_before']

        total_shifts = sum(
            shifts[worker][m] for m in ('breakfast', 'lunch', 'dinner')
        )
        scores[worker] += total_shifts * penalties['total_shifts']

        n_partners = sum(p in shifts[worker]['partners'] for p in assigned_workers)
        scores[worker] += n_partners * penalties['known_partner']

        scores[worker] += shifts[worker][meal] * penalties['same_meal']

    return scores


def create_week_plan(workers):
    shifts = init_worker_bookkeeping()
    weekplan = []

    for day in days:
        weekplan.append({})

        for meal in meals[day]:
            assigned_workers_meal = pick_workers(shifts, workers, meal, weekplan)
            weekplan[-1][meal] = list(assigned_workers_meal)

    return weekplan, shifts


def main():
    args = parser.parse_args()

    with open(args.teilnehmer) as f:
        workers = set(map(str.strip, f.read().splitlines()))

    print('Starting iteration')

    counter = 0
    max_score = max_allowed_score + 1
    while max_score > max_allowed_score:
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

        max_score = max(w['total_score'] for w in shifts.values())
        print(max_score)

    print('\n\n')
    for day, meals in zip(days, weekplan):
        print(f'{f"  {day}  ":#^30}')
        for meal, assigned_workers in meals.items():
            print('  {:15}: {}, {}, {}'.format(meal, *list(assigned_workers)))

        print()
    print()

    for w, c in sorted(shift_counts.items(), key=lambda w: w[1]):
        print(f'{w:25} {c}')


if __name__ == '__main__':
    main()
