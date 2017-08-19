import random
from collections import defaultdict
import itertools
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('teilnehmer')
parser.add_argument('--seed', type=int, default=0)

num_workers = 3

meals = defaultdict(lambda: ['breakfast', 'lunch', 'dinner'])
meals['sunday_departure'] = ['breakfast']

penalties = {
    'same_meal': {'lunch': 25, 'breakfast': 100, 'dinner': 25},
    'day_before': 50,
    'known_partner': 100,
    'total_shifts': 100,
    'same_day': 200,
    'same_semester': 10,
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


def init_worker_bookkeeping(workers, semesters):
    return {worker: {
        'semester': semester,
        'total_score': 0,
        'breakfast': 0,
        'lunch': 0,
        'dinner': 0,
        'partners': [],
        'leisure_time': 1,
    } for worker, semester in zip(workers, semesters)}


def increase_assignment(shifts, worker, assignement):
    shifts[worker][assignement] += 1


def add_partners(shifts, one, two):
    shifts[one]['partners'].append(two)
    shifts[two]['partners'].append(one)


def pick_worker(available_workers):
    return random.choice(list(available_workers))


def pick_workers(shifts, workers, meal, weekplan):
    assigned_workers = []

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
        assigned_workers.append(worker)
        shifts[worker]['total_score'] += min_score

    for w1, w2 in itertools.combinations(assigned_workers, 2):
        add_partners(shifts, w1, w2)

    for worker in assigned_workers:
        increase_assignment(shifts, worker, meal)

    return assigned_workers


def score_workers(shifts, workers, assigned_workers, meal, weekplan):
    return {
        worker: score_worker(shifts, worker, assigned_workers, meal, weekplan)
        for worker in workers
        if worker not in assigned_workers
    }


def score_worker(shifts, worker, assigned_workers, meal, weekplan):
    score = 0

    n_same_day = sum(worker in m for m in weekplan[-1].values())
    score += n_same_day * penalties['same_day']

    if len(weekplan) > 1:
        n_day_before = sum(worker in m for m in weekplan[-2].values())
        score += n_day_before * penalties['day_before']

    total_shifts = sum(
        shifts[worker][m] for m in ('breakfast', 'lunch', 'dinner')
    )
    score += total_shifts * penalties['total_shifts']

    n_partners = sum(p in shifts[worker]['partners'] for p in assigned_workers)
    score += n_partners * penalties['known_partner']

    n_same_semester = sum(
        shifts[p]['semester'] == shifts[worker]['semester']
        for p in assigned_workers
    )
    score += n_same_semester * penalties['same_semester']
    score += shifts[worker][meal] * penalties['same_meal'][meal]

    return score


def create_week_plan(workers, semesters):
    shifts = init_worker_bookkeeping(workers, semesters)
    workers = list(workers)
    weekplan = []

    for day in days:
        weekplan.append({})

        for meal in meals[day]:
            assigned_workers_meal = pick_workers(shifts, workers, meal, weekplan)
            weekplan[-1][meal] = list(assigned_workers_meal)

    return weekplan, shifts


def main():
    args = parser.parse_args()
    random.seed(args.seed)

    with open(args.teilnehmer) as f:
        workers = []
        semesters = []

        for line in f:
            line = line.strip()
            if line:
                worker, semester = line.split(',')
                workers.append(worker)
                semesters.append(semester)

    print('Starting iteration')

    counter = 0
    max_allowed_score = 255 * len(workers)
    total_score = max_allowed_score + 1
    while total_score > max_allowed_score:
        counter += 1

        print(f'Iteration {counter}')

        try:
            weekplan, shifts = create_week_plan(workers, semesters)
        except IndexError as e:
            print(e)
            continue

        total_score = sum(w['total_score'] for w in shifts.values())
        print(total_score)
        print(total_score / len(workers))

    print(f'{"Name":25} b l d total score')
    for w, c in sorted(shifts.items(), key=lambda w: w[0]):
        total = c["breakfast"] + c["lunch"] + c["dinner"]
        print(f'{w:25} {c["breakfast"]:1} {c["lunch"]:1} {c["dinner"]:1} {total:5} {c["total_score"]:5}')

    print('\n\n')
    for day, meals in zip(days, weekplan):
        print(f'{f"  {day}  ":#^30}')
        for meal, assigned_workers in meals.items():
            print(f'  {meal:15}:', end='')
            for worker in sorted(assigned_workers):
                print(f'{worker} ({shifts[worker]["semester"]})', end=', ')
            print()
        print()
    print()


if __name__ == '__main__':
    main()
