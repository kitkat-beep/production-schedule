import pandas as pd
import streamlit as st
from io import BytesIO

# Конфигурация
DAYS_IN_MONTH = 28
NORM_HOURS = 160

# Заголовки для DataFrame
columns = ["Ф.И.О. мастера смены", "ГР №"] + [str(day) for day in range(1, DAYS_IN_MONTH+1)] + ["Факт ФРВ", "от ФРВ"]

def create_schedule():
    schedule = []
    
    # Добавление сотрудников
    schedule.append(create_employee("Феоктистова Е.А.", "№1", [11.5, 11.5, "", 11.5, 11.5, "", "", "", 11.5, 11.5]))
    # ... Добавьте остальных сотрудников по аналогии
    
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