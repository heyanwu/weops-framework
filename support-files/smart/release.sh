APP_NAME=$1
VERSION=$2
cd /codes
pip install -i https://mirrors.cloud.tencent.com/pypi/simple -r /codes/support-files/smart/requirements.txt
python ./support-files/smart/smart.py release

mkdir -p /saas/$APP_NAME
mkdir -p /saas/$APP_NAME/pkgs
pip download -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple -d /saas/$APP_NAME/pkgs

mv ./app.yml /saas/$APP_NAME
touch /saas/$APP_NAME/install.txt
cp -Rf /codes /saas/$APP_NAME/src

rm -Rf /saas/$APP_NAME/src/venv
rm -Rf /saas/$APP_NAME/src/.git

cd /saas

tar -zcvf $APP_NAME-$VERSION.tar.gz $APP_NAME/

mkdir /codes/dist
mv /saas/$APP_NAME-$VERSION.tar.gz /codes/dist/$APP_NAME-$VERSION.tar.gz



