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


def remove_related_studies_from_study_list(all_studies, user):
    for study in list(all_studies):
        for own_study in user.own_studies:
            if study.id == own_study.id:
                all_studies.remove(study)
        for participated_study in user.participated_studies:
            if study.id == participated_study.id:
                all_studies.remove(study)

    return all_studies