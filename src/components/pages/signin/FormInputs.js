/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import { Link } from 'react-router-dom'
import { EmailField, PasswordField } from '../../forms/inputs'

const FormInputs = () => (
  <div>
    <input type="hidden" name="name" value="user" />
    <EmailField
      id="user-identifier"
      required
      className="mb36"
      name="identifier"
      label="Adresse e-mail"
      placeholder="Identifiant (email)"
    />
    <PasswordField
      id="user-password"
      required
      className="mb36"
      name="password"
      label="Mot de passe"
      placeholder="Mot de passe"
    />
    <Link to="/mot-de-passe-perdu" className="is-white-text is-underline fs16">
      <span>Mot de passe oublié&nbsp;?</span>
    </Link>
  </div>
)

export default FormInputs
