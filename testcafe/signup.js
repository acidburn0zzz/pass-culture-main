import { Selector, RequestLogger } from 'testcafe'

import BROWSER_ROOT_URL from './helpers/config'

var fs = require('fs')

const CONFIG_FILE_NAME = '/home/daniel/workspace/pass_culture/pass-culture-browser/testcafe/helpers/config.json'

// Reads the configuration file and parses settings from JSON.
function getConfig() {
    return JSON.parse(fs.readFileSync(CONFIG_FILE_NAME, 'utf-8'))
}
const API_URL = getConfig()

const LOGGER_URL = API_URL.url + '/users'

const logger = RequestLogger(LOGGER_URL, {
  logResponseBody: true,
  stringifyResponseBody: true,
  logRequestBody: true,
  stringifyRequestBody: true
})

const inputUsersPublicName = Selector('#input_users_publicName')
const inputUsersEmail = Selector('#input_users_email')
const inputUsersPassword = Selector('#input_users_password')
const inputUsersContactOk = Selector('#input_users_contact_ok')
const signUpButton = Selector('button')
const signInButton = Selector('.is-secondary')
const inputUsersEmailError = Selector('#input_users_email-error')
const inputUsersPasswordError = Selector('#input_users_password-error')
const inputUsersContactOkError = Selector('#input_users_contact_ok-error')

fixture `SignupPage | Création d'un compte utilisateur`
    .page `${BROWSER_ROOT_URL+'inscription'}`

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {

  await t
  .click(signInButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoire est manquant, le bouton créer est desactivé", async t => {
    await t
    .typeText(inputUsersEmail, 'email@email.test')
    .wait(1000)
    .expect(signUpButton.hasAttribute('disabled')).ok()
})

test.skip("Lorsque le user est créé, l'utilisateur est redirigé vers la page /découverte/empty", async t => {
  await t
  // TODO Comment créer un user à chaque test ?
  .typeText(inputUsersPublicName, 'Public Name')
  .typeText(inputUsersEmail, 'pctest.cafe@btmx.fr')
  .typeText(inputUsersPassword, 'password1234')
  await t.click(inputUsersContactOk)
  .click(signUpButton)
  .wait(1000)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/decouverte/empty')

})

fixture `SignupPage | Création d'un compte utilisateur | Messages d'erreur lorsque les champs ne sont pas correctement remplis`
  .page `${BROWSER_ROOT_URL+'inscription'}`

test
.requestHooks(logger)
('Case contact à cocher', async t => {
  await t
  .typeText(inputUsersPublicName, 'Public Name')
  .typeText(inputUsersEmail, 'pctest.cafe@btmx.fr')
  .typeText(inputUsersPassword, 'password1234')
  .wait(1000)
  .click(signUpButton)
  const errorMessage = logger.requests[0].response.body
  const expected = {
  "contact_ok": [
    "Vous devez obligatoirement cocher cette case"
  ]
}
  await t.expect(JSON.parse(errorMessage)).eql(expected)
  await t.expect(inputUsersContactOkError.innerText).eql(' Vous devez obligatoirement cocher cette case\n')
})

test
.requestHooks(logger)

('E-mail déjà présent dans la base et mot de passe invalide', async t => {
  await t

  .typeText(inputUsersPublicName, 'Public Name')
  .typeText(inputUsersEmail, 'pctest.cafe@btmx.fr')
  .typeText(inputUsersPassword, 'pas')
  .wait(1000)
  .click(inputUsersContactOk)
  .wait(1000)
  .click(signUpButton)
  .wait(1000)
  const errorMessage = logger.requests[0].response.body
  const expected = {
    "email": [
      "Un compte li\u00e9 \u00e0 cet email existe d\u00e9j\u00e0"
    ],
    "password": [
      "Vous devez saisir au moins 8 caract\u00e8res."
    ]
  }
  await t.expect(JSON.parse(errorMessage)).eql(expected)
  await t.expect(inputUsersEmailError.innerText).eql(" Un compte lié à cet email existe déjà\n")
  await t.expect(inputUsersPasswordError.innerText).eql(" Vous devez saisir au moins 8 caractères.\n")
})
