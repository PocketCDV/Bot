schedule = 🗓 Розклад на <b>{ $weekday }, { $schedule_date }</b>:

    { $schedule }

schedule-no-classes = 🗓 Розклад на <b>{ $weekday }, { $schedule_date }</b>:

    💤 <i>У цей день занять немає.</i>

schedule-class-entry =
    .short =
        ⏳ <b>{ $start_time } - { $end_time } | { $room }</b>
        <i><a href="{ $detail }">{ $title }</a></i>
    .detailed =
        📋 <b>{ $title }</b>

        📂 <b>Модуль:</b> { $module }
        <b>Форма занять:</b> { $form_color } { $form }

        ⌛️ <b>Дата:</b> { $date }
        <b>Тривалість:</b> { $start_time } - { $end_time }

        📍 <b>Аудиторія:</b> { $room }
        <b>Викладач:</b> { $teacher }