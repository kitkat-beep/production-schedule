import pandas as pd
import streamlit as st
from io import BytesIO

DAYS_IN_MONTH = 28
NORM_HOURS = 160
WORK_GROUPS = ['ГР1', 'ГР2', 'ГР3', 'ГР4', 'офис']

# Шаблоны графиков из файла
SCHEDULE_TEMPLATES = {
    'График1': [11.5, 11.5, "", 11.5, 11.5, "", "", "", 11.5, 11.5],
    'График2': [11.5, 7.5, "", "", 11.5, 11.5, "", 11.5, 11.5],
    'График3': ["", 11.5, 11.5, "", "", "", 11.5, 11.5],
    'График4': ["", "", 11.5, 11.5, "", 11.5, 11.5],
    'Офис': [8, 8, 8, 8, 8]
}

class EmployeeSchedule:
    def __init__(self, name, group, schedule_type, exceptions=None):
        self.name = name
        self.group = group
        self.schedule_type = schedule_type
        self.exceptions = exceptions or {}

    def generate_schedule(self):
        base_pattern = SCHEDULE_TEMPLATES[self.schedule_type]
        schedule = {}
        
        pattern_index = 0
        for day in range(1, DAYS_IN_MONTH+1):
            if day in self.exceptions:
                schedule[str(day)] = self.exceptions[day]
            else:
                schedule[str(day)] = base_pattern[pattern_index % len(base_pattern)]
                pattern_index += 1
        
        total = sum(
            float(h) if isinstance(h, (int, float, str)) and str(h).replace('.', '').isdigit() 
            else 0 
            for h in schedule.values()
        )
        
        return {
            'Ф.И.О. мастера смены': self.name,
            'ГР №': self.group,
            **schedule,
            'Факт ФРВ': total,
            'от ФРВ': total - NORM_HOURS
        }

def create_schedule():
    employees = [
        # График №1
        EmployeeSchedule("Феоктистова Е.А.", "ГР1", "График1", {12: "ГО", 27: 4}),
        EmployeeSchedule("Третьяков А.И.", "ГР1", "График1"),
        EmployeeSchedule("Грачева Т.В.", "ГР1", "График1"),
        EmployeeSchedule("Белоусов А.В.", "ГР1", "График1", {12: "ГО"}),
        EmployeeSchedule("Давыдова С.В.", "ГР1", "График1"),
        EmployeeSchedule("Саранцев А.Н. ученик", "ГР1", "График1", {6: "ув"}),

        # График №2
        EmployeeSchedule("Панфилов А.В.", "ГР2", "График2", {22: "го"}),
        EmployeeSchedule("Свиридов А.О. (стажер)", "ГР2", "График2"),
        EmployeeSchedule("Смирнов Н.Н.", "ГР2", "График2"),
        EmployeeSchedule("Синякина С.А.", "ГР2", "График2"),
        EmployeeSchedule("Пантюхин А.Д.", "ГР2", "График2", {23: "го"}),
        EmployeeSchedule("Давыдова О.И.", "ГР2", "График2"),
        EmployeeSchedule("Роменский Р.С.", "ГР2", "График2"),

        # График №3
        EmployeeSchedule("Лукашенкова С.В.", "ГР3", "График3"),
        EmployeeSchedule("Раку О.А.", "ГР3", "График3", {8: "б/л"}),
        EmployeeSchedule("Михеева А.В.", "ГР3", "График3", {15: "ГО"}),
        EmployeeSchedule("Антипенко В.Н.", "ГР3", "График3"),

        # График №4
        EmployeeSchedule("Юдина И.Е.", "ГР4", "График4"),
        EmployeeSchedule("Лисовская Т.А.", "ГР4", "График4", {4: "б/л"}),
        EmployeeSchedule("Галкина В.А.", "ГР4", "График4", {11: "б/л"}),
        EmployeeSchedule("Незбудеев Д.С.", "ГР4", "График4"),
        EmployeeSchedule("Смоляков А.А.", "ГР4", "График4", {12: "ГО"}),
        EmployeeSchedule("Долгоаршиннных Т.Р.", "ГР4", "График4"),

        # Офис
        EmployeeSchedule("Подгорбунский Д.А.", "офис", "Офис")
    ]
    
    return pd.DataFrame([e.generate_schedule() for e in employees])

# Остальной код без изменений (валидация, фильтрация, интерфейс и т.д.)
# ... (полный код из предыдущего ответа)