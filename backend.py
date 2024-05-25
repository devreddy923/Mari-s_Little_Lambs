import pandas as pd
from datetime import datetime, timedelta, time
from dateutil.relativedelta import relativedelta
import calendar
from collections import deque


class Student:
    def __init__(self, name, date_of_birth, level, schedule, program_type, start_date=None):
        self.name = name
        self.date_of_birth = date_of_birth
        self.level = level
        self.schedule = schedule
        self.program_type = program_type
        self.start_date = start_date
        self.existing_student = False
        self.promotion_date = None

    def __str__(self):
        return (f"Student(Name: {self.name}, Date of Birth: {self.date_of_birth}, Level: {self.level}, "
                f"Schedule: {self.schedule}, Program Type: {self.program_type}, Start Date: {self.start_date})")


class Classroom:
    def __init__(self, capacity_levels):
        self.capacity_levels = capacity_levels
        self.level_queues = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
        self.level_promotedQueues = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
        self.level_promotedQueues2 = {1: deque(), 2: deque(), 3: deque(), 4: deque()}
        self.students = []
        self.graduated_students = []

    def read_existing_data(self, active_file, hold_file):
        active_df = pd.read_excel(active_file, skiprows=3, header=1)
        active_df = active_df.reset_index(drop=True)
        active_df = active_df[['First Name', 'Dob', 'Room', 'Time Schedule', 'Tags']]
        active_df = active_df.rename(
            columns={'First Name': 'Name', 'Dob': 'DoB', 'Room': 'Room', 'Time Schedule': 'Schedule',
                     'Tags': 'Program Type'})
        active_df['Program Type'] = active_df['Program Type'].str.contains('FlexEd').map(
            {True: 'Flexible', False: 'Fixed'})

        hold_df = pd.read_excel(hold_file, skiprows=3, header=1)
        hold_df = hold_df.reset_index(drop=True)
        hold_df = hold_df[['First Name', 'Dob', 'Room', 'Time Schedule', 'Tags', 'Admission Date']]
        hold_df = hold_df.rename(
            columns={'First Name': 'Name', 'Dob': 'DoB', 'Room': 'Room', 'Time Schedule': 'Schedule',
                     'Tags': 'Program Type', 'Admission Date': 'Admission Date'})
        hold_df['Program Type'] = hold_df['Program Type'].str.contains('FlexEd').map({True: 'Flexible', False: 'Fixed'})

        level_dict = {'Infants': 1, 'Wobblers': 2, 'Older Toddlers': 3, 'Preschool': 4}

        def convert_days(schedule):
            day_mapping = {
                'M': 'Monday',
                'T': 'Tuesday',
                'W': 'Wednesday',
                'Th': 'Thursday',
                'F': 'Friday'
            }
            days = schedule.split(', ')
            full_day_names = [day_mapping[day.split(' ')[0]] for day in days if day.split(' ')[0] in day_mapping]
            return ','.join(full_day_names)

        active_df['Schedule'] = active_df['Schedule'].apply(convert_days).apply(lambda x: x.split(','))
        hold_df['Schedule'] = hold_df['Schedule'].apply(convert_days).apply(lambda x: x.split(','))

        for _, row in active_df.iterrows():
            if pd.notna(row['DoB']):
                student = Student(row['Name'], datetime.strptime(str(row['DoB']), '%Y-%m-%d %H:%M:%S'),
                                  level_dict[row['Room']], row['Schedule'], row['Program Type'])
                student.promotion_date = self.calculate_promotion_date(student)
                student.existing_student = True
                self.students.append(student)

        for _, row in hold_df.iterrows():
            if pd.notna(row['DoB']) and pd.notna(row['Admission Date']):
                student = Student(row['Name'], datetime.strptime(str(row['DoB']), '%Y-%m-%d %H:%M:%S'),
                                  level_dict[row['Room']], row['Schedule'], row['Program Type'],
                                  datetime.strptime(str(row['Admission Date']), '%Y-%m-%d %H:%M:%S'))
                student.promotion_date = self.calculate_promotion_date(student)
                self.level_queues[level_dict[row['Room']]].append(student)

    def calculate_daily_strength(self):
        daily_strength = {
            1: {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0},
            2: {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0},
            3: {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0},
            4: {"Monday": 0, "Tuesday": 0, "Wednesday": 0, "Thursday": 0, "Friday": 0}
        }
        for student in self.students:
            if student.existing_student and student.schedule is not None:
                for day in student.schedule:
                    daily_strength[student.level][day.strip()] += 1
        df = pd.DataFrame(daily_strength).T
        return df

    def kpi_calculate(self, level):
        total_active_students = [0] * 4
        total_hold_students = [0] * 4
        graduating_soon = [0] * 4
        for student in self.students:
            if student.level == level:
                total_active_students[level - 1] += 1
                if student.promotion_date <= (datetime.now() + timedelta(days=60)):
                    graduating_soon[level - 1] += 1
        total_hold_students[level - 1] = len(self.level_queues[level])
        return total_active_students, total_hold_students, graduating_soon

    def apply_for_admission(self, applicant, joining_date=None):
        if joining_date is None:
            joining_date = datetime.now()
        self.update_members(joining_date, None)
        level = applicant.level
        schedule = applicant.schedule
        flexible_students = [student for student in self.students if
                             student.existing_student and student.level == level and student.program_type == "Flexible"]
        if self.can_join_level(schedule, level):
            return joining_date, schedule, False
        elif flexible_students:
            return (datetime.now() + timedelta(days=32)), schedule, True
        else:
            next_dates_list = self.calculate_next_possible_dates(level, joining_date)
            for next_date in sorted(next_dates_list):
                current_age = (next_date - applicant.date_of_birth).days / 365
                if current_age > self.get_age_limit(applicant.level):
                    break
                self.update_members(next_date, None)
                if self.can_join_level(schedule, level):
                    return next_date, schedule, False
            return False, False, False

    def update_members(self, joining_date, level):
        if level is None:
            for level in range(1, 5):
                self.promote_students(level, joining_date)
                self.update_waiting_list(level)
                self.admit_students_from_waiting(level, joining_date)
        else:
            self.promote_students(level, joining_date)
            self.update_waiting_list(level)
            self.admit_students_from_waiting(level, joining_date)

    def promote_students(self, level, joining_date):
        for student in self.students:
            if student.existing_student and student.level == level and joining_date >= student.promotion_date:
                next_level = student.level + 1
                schedule = student.schedule
                if next_level < 5 and self.can_join_level(schedule, next_level):
                    student.level = next_level
                    student.promotion_date = self.calculate_promotion_date(student)
                elif next_level < 5:
                    student.level = next_level
                    student.start_date = student.promotion_date
                    student.promotion_date = self.calculate_promotion_date(student)
                    self.level_promotedQueues[student.level].append(student)
                    self.students.remove(student)
                elif student.level == 4 and joining_date >= student.promotion_date:
                    self.students.remove(student)
                    self.graduated_students.append(student)

    def update_waiting_list(self, level):
        if self.level_promotedQueues[level]:
            self.level_promotedQueues[level] = deque(
                sorted(self.level_promotedQueues[level], key=lambda x: x.start_date))
        if self.level_queues[level]:
            self.level_queues[level] = deque(sorted(self.level_queues[level], key=lambda x: x.start_date))

    def admit_students_from_waiting(self, level, joining_date):
        daily_strength = self.calculate_daily_strength()
        while all(daily_strength.loc[level] != 0):
            if self.level_promotedQueues[level]:
                student = self.level_promotedQueues[level].popleft()
                if self.can_join_level(student.schedule, level):
                    self.students.append(student)
                else:
                    self.level_promotedQueues2[level].append(student)
            elif self.level_queues[level]:
                student = self.level_queues[level].popleft()
                if student.start_date <= joining_date and self.can_join_level(student.schedule, level):
                    student.existing_student = True
                    student.promotion_date = self.calculate_promotion_date(student, student.start_date)
                    self.students.append(student)
                else:
                    self.level_promotedQueues2[level].append(student)
            else:
                break
        self.level_promotedQueues[level].extend(self.level_promotedQueues2[level])

    def can_join_level(self, schedule, level):
        level_capacity = self.capacity_levels[level - 1]
        for day in schedule:
            students_in_level = sum(1 for student in self.students if
                                    student.level == level and day.lower() in [d.lower() for d in student.schedule])
            if students_in_level >= level_capacity:
                return False
        return True

    def calculate_level(self, dob):
        age = (datetime.now() - dob).days / 365
        if 0 <= age < 1:
            return 1
        elif 1 <= age < 2:
            return 2
        elif 2 <= age < 3:
            return 3
        elif 3 <= age <= 5:
            return 4
        else:
            return None

    def calculate_next_possible_dates(self, level, joining_date):
        nextPromotedDates = []
        if level > 2:
            nextPromotedDates.extend(student.promotion_date for student in self.students if
                                     student.level == level - 2 and student.promotion_date >= joining_date)
            nextPromotedDates.extend(student.promotion_date for student in self.level_queues[level - 2] if
                                     student.promotion_date >= joining_date)
        if level > 1:
            nextPromotedDates.extend(student.promotion_date for student in self.students if
                                     student.level == level - 1 and student.promotion_date >= joining_date)
            nextPromotedDates.extend(student.promotion_date for student in self.level_queues[level - 1] if
                                     student.promotion_date >= joining_date)
        nextPromotedDates.extend(student.promotion_date for student in self.students if
                                 student.level == level and student.promotion_date >= joining_date)
        nextPromotedDates.extend(
            student.promotion_date for student in self.level_queues[level] if student.promotion_date >= joining_date)
        return nextPromotedDates

    def calculate_promotion_date(self, student, inputDate=datetime.now(), promotion_date=None):
        if promotion_date is None:
            current_level_age_limit = self.get_age_limit(student.level)
            next_level_age_limit = self.get_age_limit(student.level + 1) if student.level < 4 else 5
            current_age = (inputDate - student.date_of_birth).days / 365
            promotion_date = student.date_of_birth + relativedelta(years=current_level_age_limit)
        return promotion_date

    def get_age_limit(self, level):
        if level == 1:
            return 1
        elif level == 2:
            return 2
        elif level == 3:
            return 3
        elif level == 4:
            return 5

    def date_strength(self, level):
        current_date = datetime.now()
        end_date = current_date + timedelta(days=10)
        daily_strength = {}
        while current_date <= end_date:
            day_of_week = calendar.day_name[current_date.weekday()]
            self.update_members(current_date, level)
            count = sum(1 for student in self.students if
                        student.existing_student and student.level == level and day_of_week in student.schedule)
            daily_strength[current_date] = daily_strength.get(current_date, 0) + count
            current_date += timedelta(days=1)
        daily_data = pd.DataFrame(daily_strength, index=[level]).transpose()
        daily_data.columns = ['Strength']
        return daily_data


def process_inputs(name, dob, child_class, schedule_days, program_type, joining_date, active_file, hold_file, fte_file):
    joining_date = datetime.combine(joining_date, time())
    level_dict = {'Infants': 1, 'Wobblers': 2, 'Older Toddlers': 3, 'Preschool': 4}
    level = level_dict.get(child_class, None)

    capacity_levels = [8, 8, 7, 20]
    classroom = Classroom(capacity_levels)

    classroom.read_existing_data(active_file, hold_file)
    new_applicant = Student(name, dob, level, schedule_days, program_type)
    next_available_date, schedule, flexible = classroom.apply_for_admission(new_applicant, joining_date)
    total_active_students, total_hold_students, graduating_soon = classroom.kpi_calculate(level)
    df = classroom.calculate_daily_strength()

    fte_df = pd.read_excel(fte_file, skiprows=2, header=1)
    fte_df = fte_df.reset_index()
    fte_df['Room'] = fte_df['Room'].map(level_dict)
    fte_count = (fte_df['Total'][level].mean() * classroom.capacity_levels[level - 1])

    if next_available_date is not False:
        waittime = next_available_date - joining_date
    else:
        waittime = timedelta(days=365)
    availability = "No" if next_available_date > joining_date else "Yes"

    # Convert the dataframe to string, excluding the levels
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedule_available_str = df[days_of_week].reset_index(drop=True).to_string(index=False)

    metrics = {
        'Total kids': sum(total_active_students),
        'Capacity': classroom.capacity_levels[level - 1],
        'Number of kids on hold': sum(total_hold_students),
        'Full-time eq.': round(fte_count, 2),
        'Graduating in next 60 days': sum(graduating_soon),
        'Recently joined (coming soon)': "N/A",
        'Kid to staff ratio (coming soon)': "N/A",
        'Wait time in days': waittime.days,
        'Availability for the requested date': availability,
        'Earliest Available Date': next_available_date.strftime('%Y-%m-%d') if next_available_date else "N/A",
        'Preferred Schedule': ', '.join(schedule),
        'Schedule Available': schedule_available_str,  # Updated line to exclude levels from the dataframe
        'Flexible Notice Required': flexible
    }

    return metrics


# Example usage
if __name__ == "__main__":
    name = "John Doe"
    dob = datetime(2024, 5, 25)  # Corrected date of birth
    child_class = "Infants"
    schedule_days = ["Monday", "Wednesday"]
    program_type = "Fixed"
    joining_date = datetime(2024, 5, 25)
    active_file = "active.xlsx"
    hold_file = "hold.xlsx"
    fte_file = "fte_all_rooms.xlsx"

    metrics = process_inputs(name, dob, child_class, schedule_days, program_type, joining_date, active_file, hold_file,
                             fte_file)
    print(metrics)
