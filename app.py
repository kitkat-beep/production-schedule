import pandas as pd
import streamlit as st
from io import BytesIO

# Конфигурация
DAYS_IN_MONTH = 28
NORM_HOURS = 160

# Заголовки для DataFrame
columns = ["Ф.И.О. мастера смены", "ГР №"] + [str(day) for day in range(1, DAYS_IN_MONTH+1)] + ["Факт ФРВ", "от ФРВ"]

def create_schedule():
    employees = [
        # График №1
        EmployeeSchedule("Феоктистова Е.А.", "ГР1", "График1", {'12': "ГО", '27': 4}),
        EmployeeSchedule("Третьяков А.И.", "ГР1", "График1"),
        EmployeeSchedule("Грачева Т.В.", "ГР1", "График1"),
        EmployeeSchedule("Белоусов А.В.", "ГР1", "График1", {'12': "ГО"}),
        EmployeeSchedule("Давыдова С.В.", "ГР1", "График1"),
        EmployeeSchedule("Саранцев А.Н. ученик", "ГР1", "График1", {'6': "ув"}),

        # График №2
        EmployeeSchedule("Панфилов А.В.", "ГР2", "График2", {'22': "го"}),
        EmployeeSchedule("Свиридов А.О. (стажер)", "ГР2", "График2"),
        EmployeeSchedule("Смирнов Н.Н.", "ГР2", "График2"),
        EmployeeSchedule("Синякина С.А.", "ГР2", "График2"),
        EmployeeSchedule("Пантюхин А.Д.", "ГР2", "График2", {'23': "го"}),
        EmployeeSchedule("Давыдова О.И.", "ГР2", "График2"),
        EmployeeSchedule("Роменский Р.С.", "ГР2", "График2"),

        # График №3
        EmployeeSchedule("Лукашенкова С.В.", "ГР3", "График3"),
        EmployeeSchedule("Раку О.А.", "ГР3", "График3", {'8': "б/л"}),
        EmployeeSchedule("Михеева А.В.", "ГР3", "График3", {'15': "ГО"}),
        EmployeeSchedule("Антипенко В.Н.", "ГР3", "График3"),

        # График №4
        EmployeeSchedule("Юдина И.Е.", "ГР4", "График4"),
        EmployeeSchedule("Лисовская Т.А.", "ГР4", "График4", {'4': "б/л"}),
        EmployeeSchedule("Галкина В.А.", "ГР4", "График4", {'11': "б/л"}),
        EmployeeSchedule("Незбудеев Д.С.", "ГР4", "График4"),
        EmployeeSchedule("Смоляков А.А.", "ГР4", "График4", {'12': "ГО"}),
        EmployeeSchedule("Долгоаршиннных Т.Р.", "ГР4", "График4"),

        # Офис
        EmployeeSchedule("Подгорбунский Д.А.", "офис", "Офис")
    ]
    return pd.DataFrame(schedule, columns=columns)

def create_employee(name, group, hours_pattern):
    employee = {"Ф.И.О. мастера смены": name, "ГР №": group}
    
    # Генерация графика по шаблону
    day = 1
    for hour in hours_pattern * 3:  # Повторяем шаблон для полного месяца
        if day > DAYS_IN_MONTH: break
        employee[str(day)] = hour
        day += 1
    
    # Расчет ФРВ
    total = sum([h for h in employee.values() if isinstance(h, (int, float))])
    employee["Факт ФРВ"] = total
    employee["от ФРВ"] = total - NORM_HOURS
    
    return employee

# Streamlit интерфейс
def main():
    st.title("Генератор графиков работы цеха МиЖ ГЛФ")
    
    # Создание графика
    schedule_df = create_schedule()
    
    # Отображение данных
    st.dataframe(schedule_df.fillna(""), height=800)
    
    # Экспорт в Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        schedule_df.to_excel(writer, index=False)
    
    st.download_button(
        label="Скачать Excel",
        data=output.getvalue(),
        file_name="production_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()