from database import crud


def get_user_study_relation(db, study, user):
    # Check if the user is the creator of the study
    if user.id == study.user_id:
        return 'creator'

    # Check if the user is invited to the study
    if crud.get_invitation_by_user_and_study(db, user.id, study.id):
        return 'invited'

    # Check if the user is participated in the study
    if crud.check_participant_in_study(db, user.id, study.id):
        return 'participant'

    # If the user is none of the above, it is just a visitor
    return 'visitor'
