# /settings
# /rules 
# /info @user 
# /warn @user [причина] 
# /mute @user [время] 
# /unmute @user 
# /ban @user [причина] 
# /unban @user 
# /clear [N] 
# /pin 
# /unpin
# /antispam on/off
# /logs [параметры]
# /remind @user [текст] [время]
# /ai [вопрос]
# /stats
# /role @user [роль]
# /backup
# /random [список]
# /translate [язык] [текст]

class Help_Commands:    
    class Basic:
        backup = '/backup'
        random = '/random'
        translate = '/translate'
        stats = '/stats'
        remind = '/remind'
        logs = '/logs'
        settings = '/settings'
        unpin = '/unpin'
        pin = '/pin'
        clear = '/clear'
        rules = '/rules'        
    
    class AIComponents:
        ai = '/ai'
        antispam = '/antispam'
    
    class MoveWUsers:
        info = '/info'
        ba = '/ban'
        unban = '/unban'
        mute = '/mute'
        unmute = '/unmute'
        warn = '/warn'
        role = '/role'

