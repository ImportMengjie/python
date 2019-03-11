import datetime
import csv
import copy

# Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private
# 12h 1d 2d 4d 7d 15d


class Date():
    review_day = [0.5, 1, 2, 4, 7, 15]
    space_times = [int(i*4) for i in review_day]
    state_name = {0: '上午', 1: '下午', 2: '晚上'}

    def __init__(self, start_date: datetime.date, start_state: int):
        self.start_date = (start_date, start_state)
        self.date = start_date
        self.state = start_state
        self.review_date = [self.from_space_times_get_date(
            i) for i in Date.space_times]

    def from_space_times_get_date(self, space_times: int):
        total_state = space_times+self.start_date[1]
        state = total_state % 3
        date = self.start_date[0] + datetime.timedelta(total_state//3)
        return (date, state)

    # def cmp(self, other):
    #     return self.date < other.date if self.date != other.date else self.state <= other.state

    def get_next_subject_date(self):
        return Date(self.date+datetime.timedelta(1), self.state)


class Schedule():
    csv_header = ['Subject', 'Start Date',
                  'Start Time', 'End Date', 'End Time']
    state_time = {0: ('08:00', '12:00'), 1: (
        '12:00', '17:30'), 2: ('19:00', '23:30')}

    def __init__(self, subjects: list, start_date: Date, step: int):
        self.subjects = subjects
        self.start_date = start_date
        self.step = step
        self.subjects_date = []
        self.map_date_subject = {}
        temp = start_date
        for idx, subject in enumerate(subjects):
            self.subjects_date.append((subject, temp))
            if temp.start_date not in self.map_date_subject:
                self.map_date_subject[temp.start_date] = []
            self.map_date_subject[temp.start_date].append(subject)
            for review_date in temp.review_date:
                if review_date not in self.map_date_subject:
                    self.map_date_subject[review_date] = []
                self.map_date_subject[review_date].append(subject)
            if idx % step == 0 and idx != 0:
                temp = temp.get_next_subject_date()
        self.sorted_key = sorted(self.map_date_subject.keys(
        ), key=lambda x: (x[0], x[1]))

    def get_csv_next_subject(self, idx: int):
        if idx >= len(self.sorted_key):
            return None
        else:
            date = self.sorted_key[idx]
            subjects = self.map_date_subject[date]
            subjects_str = ';'.join(subjects)
            return [subjects_str, date[0], Schedule.state_time[date[1]][0], date[0], Schedule.state_time[date[1]][1]]


def get_total_subject(subjects_name: list):
    subjects = []
    for subject in subjects_name:
        subject_name = subject.split(' ')[0]
        subject_name += ' {}'
        start_and_end = subject.split(' ')[1].split('-')
        ''.format
        start = int(start_and_end[0])
        end = int(start_and_end[1])
        subjects.extend([subject_name.format(i) for i in range(start, end+1)])
    return subjects


if __name__ == '__main__':
    subject_bikao = '必考词 1-26'
    subject_base = '基础词 1-30'
    output_csv_path = 'schedule.csv'
    subjects = get_total_subject([subject_bikao, subject_base])
    start_date = Date(datetime.date(2018, 7, 25), 2)
    schedule = Schedule(subjects, start_date, 3)
    idx = 0
    output_list = []
    while True:
        temp = schedule.get_csv_next_subject(idx)
        if temp is not None:
            output_list.append(temp)
        else:
            break
        idx += 1
    with open(output_csv_path, 'w') as f:
        csv_f = csv.writer(f)
        csv_f.writerow(Schedule.csv_header)
        csv_f.writerows(output_list)
