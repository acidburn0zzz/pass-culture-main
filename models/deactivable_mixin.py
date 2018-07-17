""" deactivable mixin """
from sqlalchemy import Boolean, Column
from sqlalchemy.sql import expression


class DeactivableMixin(object):
    isActive = Column(Boolean,
                      nullable=False,
                      server_default=expression.true(),
                      default=True)

    @property
    def queryActive(self):
        return self.query.filter_by(isActive=True)
