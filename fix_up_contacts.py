import re
import dateutil.parser

from googly import PeopleAPI

CANON = re.compile(r'\+1(\d\d\d)(\d\d\d)(\d\d\d\d)')
COMMA = re.compile(r'(.*), (.*)')

api = PeopleAPI()

# TODO: Remove exclamation points
# TODO: Reclassify email types
# TODO: Sort email addresses
# TODO: Merge

for contact in api.get_contact_list(['names', 'phoneNumbers', 'emailAddresses', 'birthdays']):
    changed = set()
    names = contact.get('names', [])
    if names:
        for name_entry in names:
            name = name_entry.get('displayName', '')
            m = COMMA.match(name)
            if m:
                new_name = m.group(2) + ' ' + m.group(1)
                changed.add('names')
                names[0]['displayName'] = new_name
                names[0]['unstructuredName'] = new_name
                name = new_name

            if '  ' in name:
                new_name = name.replace('  ', ' ')
                changed.add('names')
                names[0]['displayName'] = new_name
                names[0]['unstructuredName'] = new_name
                name = new_name

        name = names[0].get('displayName', '')
    else:
        name = ''

    # Check Phone Numbers
    phones = contact.get('phoneNumbers', [])
    if len(phones) > 1:
        # Remove duplicate canonical numbers
        canon = set([x['canonicalForm'] for x in phones])
        if len(phones) != len(canon):
            to_remove = []
            for i, value in enumerate(phones):
                for j in range(i + 1, len(phones)):
                    if j in to_remove:
                        continue
                    if value['canonicalForm'] == phones[j]['canonicalForm']:
                        to_remove.append(j)
            if to_remove:
                for index in sorted(to_remove, reverse=True):
                    phones.pop(index)

                changed.add('phoneNumbers')

    # Put phone numbers in canonical form
    for phone in phones:
        m = CANON.match(phone.get('canonicalForm', ''))
        if m:
            new_phone = '({}) {}-{}'.format(*m.groups())
            if phone['value'] != new_phone:
                phone['value'] = new_phone
                changed.add('phoneNumbers')

    # Format Birthdays
    for birthday in contact.get('birthdays', []):
        if 'date' in birthday:
            continue
        if 'text' not in birthday:
            continue
        text = birthday['text']
        dt = dateutil.parser.parse(text)
        birthday['date'] = {'month': dt.month, 'day': dt.day}
        if dt.year != 2021:
            birthday['date']['year'] = dt.year
        changed.add('birthdays')

    if changed:
        new_value = {}
        for key in changed:
            new_value[key] = contact[key]
        keys = ', '.join(changed)
        print(f'Rewriting {name}\'s {keys}')
        api.update_contact(contact['resourceName'], contact['etag'], **new_value)
