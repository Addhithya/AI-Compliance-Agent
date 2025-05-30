from utils.auth import authenticate_gmail

def get_or_create_label(service, label_name):
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    for label in labels:
        if label['name'] == label_name:
            return label['id']

    # Create label if not found
    label_obj = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    label = service.users().labels().create(userId='me', body=label_obj).execute()
    return label['id']

def label_email(msg_id, compliant):
    service = authenticate_gmail()
    
    if compliant == True or compliant == "Yes":  # Handle both boolean and string
        label_name = 'Compliant'
        remove_label = 'Non-Compliant'
    else:
        label_name = 'Non-Compliant'
        remove_label = 'Compliant'
    
    add_label_id = get_or_create_label(service, label_name)
    remove_label_id = get_or_create_label(service, remove_label)
    
    # First, get current labels on the message to check what to remove
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        current_label_ids = message.get('labelIds', [])
        
        # Only remove label if it's currently applied
        body = {'addLabelIds': [add_label_id]}
        if remove_label_id in current_label_ids:
            body['removeLabelIds'] = [remove_label_id]
        
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body=body
        ).execute()
        
    except Exception as e:
        print(f"Error labeling message {msg_id}: {e}")
        # Fallback: just add the label without removing
        try:
            service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'addLabelIds': [add_label_id]}
            ).execute()
        except Exception as e2:
            print(f"Fallback labeling also failed for {msg_id}: {e2}")