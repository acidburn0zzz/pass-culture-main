import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/request'

class SubmitButton extends Component {
  onSubmitClick = () => {
    const { form, requestData } = this.props
    requestData('POST', 'offers', { data: form })
  }
  render () {
    return (
      <button className='button button--alive'
        onClick={this.onSubmitClick}
      >
        Soumettre
      </button>
    )
  }
}

export default connect(({ form }) => ({ form }),
  { requestData })(SubmitButton)
