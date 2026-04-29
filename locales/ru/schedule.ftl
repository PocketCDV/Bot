schedule = 🗓 Расписание на <b>{ $weekday }, { $schedule_date }</b>:

    { $schedule }

schedule-no-classes = 🗓 Расписание на <b>{ $weekday }, { $schedule_date }</b>:

    💤 <i>В этот день занятий нет.</i>

schedule-class-entry =
    .short =
        ⏳ <b>{ $start_time } - { $end_time } | { $room }</b>
        <i><a href="{ $detail }">{ $title }</a></i>
    .detailed =
        📋 <b>{ $title }</b>

        📂 <b>Модуль:</b> { $module }
        <b>Форма занятий:</b> { $form }

        ⌛️ <b>Дата:</b> { $date }
        <b>Продолжительность:</b> { $start_time } - { $end_time }

        📍 <b>Аудитория:</b> { $room }
        <b>Преподаватель:</b> { $teacher }