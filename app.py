import pandas as pd
import streamlit as st
from io import BytesIO

# Конфигурация
DAYS_IN_MONTH = 28
NORM_HOURS = 160
WORK_GROUPS = ['ГР1', 'ГР2', 'ГР3', 'ГР4', 'офис']

# Шаблоны графиков
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
            day_str = str(day)
            if day_str in self.exceptions:
                schedule[day_str] = self.exceptions[day_str]
            else:
                schedule[day_str] = base_pattern[pattern_index % len(base_pattern)]
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
            'Факт ФРВ': round(total, 1),
            'от ФРВ': round(total - NORM_HOURS, 1)
        }

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
    
    return pd.DataFrame([e.generate_schedule() for e in employees])

def validate_data(df):
    errors = []
    valid_marks = ['', 'ГО', 'б/л', 'ув', 'го']
    for idx, row in df.iterrows():
        for day in range(1, DAYS_IN_MONTH+1):
            value = row[str(day)]
            if not (isinstance(value, (int, float)) or (str(value) in valid_marks)):
                errors.append(f"Ошибка: {row['Ф.И.О. мастера смены']} день {day} - некорректное значение '{value}'")
    return errors

def main():
    st.set_page_config(layout="wide")
    st.title("📅 График работы цеха МиЖ ГЛФ")
    
    # Генерация данных
    schedule_df = create_schedule()
    
    # Фильтрация
    st.sidebar.header("Фильтры")
    selected_groups = st.sidebar.multiselect("Группы", WORK_GROUPS)
    show_overtime = st.sidebar.checkbox("Только переработки")
    
    # Применение фильтров
    if selected_groups:
        schedule_df = schedule_df[schedule_df['ГР №'].isin(selected_groups)]
        
    if show_overtime:
        schedule_df = schedule_df[schedule_df['от ФРВ'] > 0]
    
    # Валидация
    errors = validate_data(schedule_df)
    if errors:
        st.error("Найдены ошибки в данных:")
        for error in errors:
            st.write(f"⚠️ {error}")
    
    # Визуализация
    st.header("Табель учета рабочего времени")
    styled_df = schedule_df.style.applymap(
        lambda x: 'background-color: #FFE4E1' if isinstance(x, (int, float)) and x > NORM_HOURS else '',
        subset=[str(d) for d in range(1, DAYS_IN_MONTH+1)]
    )
    st.dataframe(styled_df, height=800, use_container_width=True)
    
    # Аналитика
    st.subheader("Статистика")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Всего сотрудников", len(schedule_df))
    with col2:
        avg_hours = schedule_df['Факт ФРВ'].mean()
        st.metric("Среднее время", f"{avg_hours:.1f} ч")
    with col3:
        overtime_count = len(schedule_df[schedule_df['от ФРВ'] > 0])
        st.metric("С переработкой", f"{overtime_count} чел")
    
    # Экспорт
    st.sidebar.header("Экспорт")
    export_format = st.sidebar.selectbox("Формат", ["Excel", "CSV"])
    
    if st.sidebar.button("Скачать"):
        output = BytesIO()
        if export_format == "Excel":
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                schedule_df.to_excel(writer, index=False)
            mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            file_ext = "xlsx"
        else:
            output.write(schedule_df.to_csv(index=False).encode('utf-8'))
            mime_type = "text/csv"
            file_ext = "csv"
        
        st.sidebar.download_button(
            label=f"Скачать ({export_format})",
            data=output.getvalue(),
            file_name=f"график_работы.{file_ext}",
            mime=mime_type
        )

if __name__ == "__main__":
    main()