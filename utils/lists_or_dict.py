from keyborads.button_class.root_classes import Help_Commands


help_list = [
 '/settings',
 '/rules',
 '/info',
 '/warn', 
 '/mute', 
 '/unmute', 
 '/ban', 
 '/unban', 
 '/clear', 
 '/pin', 
 '/unpin',
 '/antispam on/off',
 '/logs',
 '/remind',
 '/ai [вопрос]',
 '/stats',
 '/role',
 '/backup',
 '/random',
 '/translate',
 ]

help_class = {
    Help_Commands.Basic.settings: "Команда /settings - Открывает настройки бота.",
    Help_Commands.Basic.rules: "Команда /rules - Показывает правила группы.",
    Help_Commands.MoveWUsers.info: "Команда /info - Показывает информацию о пользователе.",
    Help_Commands.MoveWUsers.warn: "Команда /warn - Выдает предупреждение пользователю.",
    Help_Commands.MoveWUsers.mute: "Команда /mute - Отключает возможность писать сообщения.",
    Help_Commands.MoveWUsers.unmute: "Команда /unmute - Разрешает писать сообщения.",
    Help_Commands.MoveWUsers.ban: "Команда /ban - Блокирует пользователя.",
    Help_Commands.MoveWUsers.unban: "Команда /unban - Разблокирует пользователя.",
    Help_Commands.Basic.clear: "Команда /clear - Очищает сообщения.",
    Help_Commands.Basic.pin: "Команда /pin - Закрепляет сообщение.",
    Help_Commands.Basic.unpin: "Команда /unpin - Открепляет сообщение.",
    Help_Commands.AIComponents.antispam + " on/off": "Команда /antispam on/off - Включает или выключает антиспам.",
    Help_Commands.Basic.logs: "Команда /logs - Показывает логи.",
    Help_Commands.Basic.remind: "Команда /remind - Создает напоминание.",
    Help_Commands.AIComponents.ai + " [вопрос]": "Команда /ai [вопрос] - Отвечает на вопрос с использованием AI.",
    Help_Commands.Basic.stats: "Команда /stats - Показывает статистику.",
    Help_Commands.MoveWUsers.role: "Команда /role - Назначает роль пользователю.",
    Help_Commands.Basic.backup: "Команда /backup - Создает резервную копию данных.",
    Help_Commands.Basic.random: "Команда /random - Выбирает случайный элемент.",
    Help_Commands.Basic.translate: "Команда /translate - Переводит текст.",
}

admin_ru = [
    'cоздатель',
    'creator',
    'владелец',
    'Владелец',
    'Creator',
    'Cоздатель'
]