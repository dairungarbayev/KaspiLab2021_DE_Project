from abc import ABC


class TransactionStatus(ABC):

    PENDING: str = "pending"
    FULFILLED: str = "fulfilled"

    '''
    More status properties can be added, 
    such as, for example, CANCELLED (REFUNDED), DENIED, REQUESTED, AUTHORISED, etc.
    
    However, the scope of this project does not allow for 
    simulating such complex scenarios.
    '''
