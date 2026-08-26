import sys
c = 0
n = 0
try:
    with open('jobs.json', 'r', encoding='utf-8') as f:
        for line in f:
            c += line.count('"role_id"')
            n += line.count('"is_new": true')
    print(c, n)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
