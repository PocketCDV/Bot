schedule = 🗓 Schedule for <b>{ $weekday }, { $schedule_date }</b>:

    { $schedule }

schedule-no-classes = 🗓 Schedule for <b>{ $weekday }, { $schedule_date }</b>:

    💤 <i>You have no classes on this day.</i>

schedule-class-entry =
    .short =
        ⏳ <b>{ $start_time } - { $end_time } | { $room }</b>
        <i><a href="{ $detail }">{ $title }</a></i>
    .detailed =
        📋 <b>{ $title }</b>

        📂 <b>Module:</b> { $module }
        <b>Form of classes:</b> { $form }

        ⌛️ <b>Date:</b> { $date }
        <b>Duration:</b> { $start_time } - { $end_time }

        📍 <b>Room:</b> { $room }
        <b>Lecturer:</b> { $teacher }