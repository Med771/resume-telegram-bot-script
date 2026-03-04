class ProfileLexicon:
    PROFILE_STUDENT_MSG: str = (
        "👤 <b>Ваш профиль (студент)</b>\n\n"
        "🧑 <b>Имя:</b> {full_name}\n"
        "🎯 <b>Специальность:</b> {speciality}\n"
        "📚 <b>Курс:</b> {course}\n"
        "💼 <b>Занятость:</b> {busyness}\n"
        "🏙 <b>Город:</b> {city}\n"
        "📧 <b>Email:</b> {email}\n"
        "📱 <b>Телефон:</b> {phone}"
    )

    PROFILE_RECRUITER_MSG: str = (
        "👤 <b>Ваш профиль (работодатель)</b>\n\n"
        "🏢 <b>Компания:</b> {company_name}\n"
        "🧑 <b>Контакт:</b> {full_name}\n"
        "📧 <b>Email:</b> {email}\n"
        "📱 <b>Телефон:</b> {phone}"
    )

    PROFILE_EMPTY_MSG: str = (
        "⚠️ <b>Профиль не найден</b>\n\n"
        "Проверьте синхронизацию аккаунта и попробуйте снова."
    )
