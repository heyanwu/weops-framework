import jinja2
import fire


def release(app_code='weops-framework', app_name='weops-framework',
            author='canway', category='运维工具',
            introduction='weops-framework', version='1.0.0',
            memory=512):
    template_loader = jinja2.FileSystemLoader('.')
    template_env = jinja2.Environment(loader=template_loader)

    pkgs = {}
    with open('./requirements.txt', "r", encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] == "#":
                continue
            values = line.split("==")
            if len(values) != 2:
                continue
            pkgs[values[0]] = values[1]

    dynamic_dict = {
        'app_code': app_code,
        'app_name': app_name,
        'author': author,
        'category': category,
        'introduction': introduction,
        'version': version,
        'memory': memory,
        'pkgs': pkgs
    }
    app_template = template_env.get_template('support-files/smart/templates/app.yml')
    with open('./app.yml', "w", encoding='utf-8') as f:
        app = app_template.render(dynamic_dict)
        f.writelines(app)


if __name__ == '__main__':
    fire.Fire()
