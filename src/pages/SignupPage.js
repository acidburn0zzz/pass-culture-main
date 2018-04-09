import get from 'lodash.get'
import React from 'react'
import { NavLink } from 'react-router-dom'

import FormField from '../components/FormField'
import SubmitButton from '../components/SubmitButton'
import withSign from '../hocs/withSign'
import { NEW } from '../utils/config'

const SignupPage = ({ errors }) => {
  return (
    <main className='page sign-page'>
      <p>Une minute pour créer un compte, et puis c'est tout !</p>
      <form>
        <FormField className='mb3 input'
                   label={<span>Nom ou pseudo : <small>(c'est lui que verront les autres utilisateurs)</small></span>}
                   required='true'
                   collectionName='users'
                   name='publicName'
                   autoComplete='name'
                   placeholder='Rosa'
                   type='text' />
        <FormField className='mb3 input'
                   label={<span>Adresse email : <small>(pour se connecter et récupérer son mot de passe en cas d'oubli)</small></span>}
                   collectionName='users'
                   required='true'
                   autoComplete='email'
                   name='email'
                   type='email'
                   placeholder='rose@domaine.fr' />
        <FormField label={<span>Mot de passe : <small>(pour se connecter)</small></span>}
                   collectionName='users'
                   required='true'
                   autoComplete='new-password'
                   name='password'
                   placeholder='mot de passe'
                   type='password' />
      </form>
      <div className='errors'>{errors}</div>
      <footer className='flex items-center'>
        <NavLink to='/connexion'>
          Déjà inscrit ?
        </NavLink>
        <SubmitButton
          text='OK'
          className='button button--secondary'
          getBody={form => form.usersById[NEW]}
          getIsDisabled={form => !get(form, 'usersById._new_.publicName') ||
            !get(form, 'usersById._new_.email') ||
            !get(form, 'usersById._new_.password')}
          path='users'
          storeKey='users' />
      </footer>
    </main>
  )
}

export default withSign(SignupPage)
