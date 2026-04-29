schedule = 🗓 Plan na <b>{ $weekday }, { $schedule_date }</b>:

    { $schedule }

schedule-no-classes = 🗓 Plan na <b>{ $weekday }, { $schedule_date }</b>:

    💤 <i>W tym dniu nie masz zajęć.</i>

schedule-class-entry =
    .short =
        ⏳ <b>{ $start_time } - { $end_time } | { $room }</b>
        <i><a href="{ $detail }">{ $title }</a></i>
    .detailed =
        📋 <b>{ $title }</b>

        📂 <b>Moduł:</b> { $module }
        <b>Forma zajęć:</b> { $form }

        ⌛️ <b>Data:</b> { $date }
        <b>Czas trwania:</b> { $start_time } - { $end_time }

        📍 <b>Sala:</b> { $room }
        <b>Prowadzący:</b> { $teacher }