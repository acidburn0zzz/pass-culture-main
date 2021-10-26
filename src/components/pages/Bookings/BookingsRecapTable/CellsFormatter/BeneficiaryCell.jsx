/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

const BeneficiaryCell = ({ beneficiaryInfos }) => {
  const beneficiaryName = beneficiaryInfos.lastname.concat(' ', beneficiaryInfos.firstname)
  return (
    <div>
      <span>
        {beneficiaryName}
      </span>
      <br />
      <span className="beneficiary-subtitle">
        {beneficiaryInfos.email}
      </span>
      <br />
      {beneficiaryInfos.phonenumber && (
        <span className="beneficiary-subtitle">
          {beneficiaryInfos.phonenumber}
        </span>
      )}
    </div>
  )
}

BeneficiaryCell.propTypes = {
  beneficiaryInfos: PropTypes.shape({
    email: PropTypes.string.isRequired,
    firstname: PropTypes.string.isRequired,
    lastname: PropTypes.string.isRequired,
    phonenumber: PropTypes.string,
  }).isRequired,
}

export default BeneficiaryCell
