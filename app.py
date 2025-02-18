import pandas as pd
import streamlit as st
from io import BytesIO

# Конфигурация
DAYS_IN_MONTH = 28
NORM_HOURS = 160
WORK_GROUPS = ['ГР1', 'ГР2', 'ГР3', 'ГР4', 'офис']

# Базовые шаблоны графиков
SCHEDULE_TEMPLATES = {
    'default': [11.5, 11.5, "", 11.5, 11.5],
    'alternate': [11.5, 7.5, "", "", 11.5],
    'office': [8, 8, 8, 8, 8]
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
        
        for day in range(1, DAYS_IN_MONTH+1):
            if day in self.exceptions:
                schedule[str(day)] = self.exceptions[day]
            else:
                schedule[str(day)] = base_pattern[(day-1) % len(base_pattern)]
        
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
        EmployeeSchedule("Феоктистова Е.А.", "ГР1", "default", 
                        {12: "ГО", 27: 4}),
        EmployeeSchedule("Панфилов А.В.", "ГР2", "alternate",
                        {22: "го"}),
        # Добавьте остальных сотрудников по аналогии
    ]
    
    return pd.DataFrame([e.generate_schedule() for e in employees])

def validate_data(df):
    errors = []
    for idx, row in df.iterrows():
        for day in range(1, DAYS_IN_MONTH+1):
            value = row[str(day)]
            if not (isinstance(value, (int, float)) and value not in ['', 'ГО', 'б/л', 'ув']:
                errors.append(f"Некорректное значение {value} у {row['Ф.И.О. мастера смены']} в день {day}")
    return errors

def main():
    st.title("Умный график работы цеха МиЖ ГЛФ")
    
    # Фильтрация
    st.sidebar.header("Фильтры")
    selected_groups = st.sidebar.multiselect("Выберите группы", WORK_GROUPS)
    show_overtime = st.sidebar.checkbox("Показать только переработки")
    
    # Генерация данных
    schedule_df = create_schedule()
    
    # Валидация
    validation_errors = validate_data(schedule_df)
    if validation_errors:
        st.error("Обнаружены ошибки в данных:")
        for error in validation_errors:
            st.write(f"• {error}")
    
    # Применение фильтров
    if selected_groups:
        schedule_df = schedule_df[schedule_df['ГР №'].isin(selected_groups)]
    
    if show_overtime:
        schedule_df = schedule_df[schedule_df['от ФРВ'] > 0]
    
    # Визуализация
    st.header("График работы")
    styled_df = schedule_df.style.applymap(
        lambda x: 'background-color: #ffcccc' if isinstance(x, (int, float)) and x > NORM_HOURS else '',
        subset=[str(d) for d in range(1, DAYS_IN_MONTH+1)]
    )
    st.dataframe(styled_df, height=800)
    
    # Аналитика
    st.header("Аналитика")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Общее количество сотрудников", len(schedule_df))
    with col2:
        avg_overtime = schedule_df['от ФРВ'].mean()
        st.metric("Средняя переработка", f"{avg_overtime:.1f} ч")
    
    # Уведомления
    overtime_employees = schedule_df[schedule_df['от ФРВ'] > 0]
    if not overtime_employees.empty:
        st.warning(f"Переработка обнаружена у {len(overtime_employees)} сотрудников!")
    
    # Экспорт
    st.sidebar.header("Экспорт данных")
    export_format = st.sidebar.selectbox("Формат экспорта", ["Excel", "CSV"])
    
    if st.sidebar.button("Экспортировать данные"):
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
            label=f"Скачать {export_format}",
            data=output.getvalue(),
            file_name=f"schedule.{file_ext}",
            mime=mime_type
        )

if __name__ == "__main__":
    main()