schedule = 🗓 все что можно проебать в <b>{ $weekday }, { $schedule_date }</b>:

    { $schedule }

schedule-no-classes = 🗓 все что можно проебать в <b>{ $weekday }, { $schedule_date }</b>:

    💤 <i>нихера и так нет, иди спать.</i>

schedule-class-entry =
    .short =
        ⏳ <b>{ $start_time } - { $end_time } | { $room }</b>
        <i><a href="{ $detail }">{ $title }</a></i>
    .detailed =
        📋 <b>{ $title }</b>

        📂 <b>мудоль:</b> { $module }
        <b>че за пара:</b> { $form_color } { $form }

        ⌛️ <b>когда:</b> { $date }
        <b>во сколько:</b> { $start_time } - { $end_time }

        📍 <b>комыра:</b> { $room }
        <b>препод:</b> { $teacher }