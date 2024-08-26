from pprint import pprint

ONE_YEAR_IN_SECONDS = 365 * 24 * 3600
BLOCK_TIMESTAMP = 0


class VestingBoost:
    """
    A class to manage and track the vesting process of tokens with boost functionality.

    Attributes
    ----------
    remain_vest_token : int
        The amount of tokens remaining to be vested.
    total_boost_token : int
        The total amount of tokens added for boosting the vesting process.
    total_vested : int
        The total amount of tokens that have been vested.
    speed : float
        The current vesting token PER SECONDS of the vesting process.
    boost_weight : float
        The weight assigned to the boost tokens.
    total_duration_seconds : int
        The total duration for the vesting process, initialized to two years.
    last_update_time : int
        The last recorded timestamp when the state was updated.
    claimed_amount : int
        The amount of vested tokens that have been claimed.
    claimable_boost_token : int
        The amount of boost tokens that can be claimed.
    claimable_vested_token : int
        The amount of vested tokens that can be claimed.
    """

    def __init__(self, initial_vesting: int):
        """
        Initializes the VestingBoost class with the initial vesting amount.

        Parameters
        ----------
        initial_vesting : int
            The initial amount of tokens to be vested.
        """
        self.remain_vest_token = initial_vesting
        self.total_boost_token = 0
        self.total_vested = 0
        self.speed = 0
        self.boost_weight = 0
        self.total_duration_seconds = ONE_YEAR_IN_SECONDS * 2
        self.last_update_time = BLOCK_TIMESTAMP
        self.claimed_amount = 0

        self.claimable_boost_token = 0
        self.claimable_vested_token = 0

        self._update_vesting_speed()

    def _reset_state(self):
        """
        Resets the internal state after all tokens have been vested.
        Updates claimable tokens and resets vesting parameters.
        """
        self.claimable_boost_token += self.total_boost_token
        self.claimable_vested_token += self.total_vested - self.claimed_amount

        self.remain_vest_token = 0
        self.total_boost_token = 0
        self.total_vested = 0
        self.speed = 0
        self.boost_weight = 0
        self.total_duration_seconds = ONE_YEAR_IN_SECONDS * 2
        self.last_update_time = BLOCK_TIMESTAMP
        self.claimed_amount = 0

    def cal_state_update(self):
        """
        Calculates the new vesting amount and boost weight based on the elapsed time.

        Returns
        -------
        tuple
            A tuple containing the new vested amount and the new boost weight.
        """
        time_elapsed = BLOCK_TIMESTAMP - self.last_update_time
        new_vested = min(self.speed * time_elapsed, self.remain_vest_token)
        new_boost_weight = self.total_boost_token * ((self.total_vested + new_vested) / (self.remain_vest_token + self.total_vested))
        return new_vested, new_boost_weight

    def _update_state(self):
        """
        Updates the internal vesting state based on the elapsed time.
        This method is impure as it modifies the state of the object.
        """
        if self.last_update_time < BLOCK_TIMESTAMP:
            new_vested, new_boost_weight = self.cal_state_update()
            self.total_vested += new_vested
            self.remain_vest_token -= new_vested
            self.boost_weight = new_boost_weight
            self.last_update_time = BLOCK_TIMESTAMP

    def _update_vesting_speed(self):
        """
        Updates the vesting speed (S) based on the current vesting state and boost weight.
        This method is impure as it modifies the state of the object.
        """
        multiplier = (self.remain_vest_token + self.boost_weight) / self.remain_vest_token  # Boost multiplier
        self.speed = multiplier * (self.remain_vest_token / self.total_duration_seconds)  # vesting speed

    def boost(self, boost_amount: int):
        """
        Adds the specified amount of tokens to boost the vesting process.

        Parameters
        ----------
        boost_amount : int
            The amount of tokens to be added for boosting.

        Raises
        ------
        AssertionError
            If no tokens are available to boost or the boost amount exceeds the allowable limit.
        """
        assert self.remain_vest_token > 0, "No tokens to boost"
        assert self.remain_vest_token + self.total_vested >= self.total_boost_token + boost_amount, "Boost amount cannot exceed the total vesting amount"

        # Update the state
        self._update_state()

        # Handle boost
        self.total_boost_token += boost_amount
        self.boost_weight += boost_amount

        # Update the vesting speed
        self._update_vesting_speed()

    def add_vesting(self, additional_vesting: int):
        """
        Adds additional tokens to be vested during the ongoing vesting process.

        Parameters
        ----------
        additional_vesting : int
            The amount of additional tokens to be vested.
        """
        # Update the state
        self._update_state()

        if self.remain_vest_token == 0:
            self._reset_state()

        self.remain_vest_token += additional_vesting
        self._update_vesting_speed()

    def adjust_time(self, additional_seconds: int):
        """
        Adjusts the elapsed time, simulating a change in the vesting process timeline.

        Parameters
        ----------
        additional_seconds : int
            The number of seconds to advance in the vesting process.
        """
        global BLOCK_TIMESTAMP
        BLOCK_TIMESTAMP += additional_seconds

    def get_current_state(self):
        """
        Returns the current vesting status based on the adjusted elapsed time.

        Returns
        -------
        dict
            A dictionary containing the current state of the vesting process, including
            remaining vested tokens, total boost tokens, boost weight, total vested tokens,
            available tokens to claim, and current vesting speed.
        """
        total_vested = 0
        remain_vest = self.total_vested
        boost_weight = self.boost_weight

        if self.last_update_time < BLOCK_TIMESTAMP:
            new_vested, new_boost_weight = self.cal_state_update()
            total_vested += new_vested
            remain_vest -= new_vested
            boost_weight = new_boost_weight

        available_to_claim = total_vested - self.claimed_amount

        return {
            "Remain Vest": remain_vest,
            "Total Boost Token": self.total_boost_token,
            "Weight": boost_weight,
            "Total Vested": total_vested,
            "Available to claim": available_to_claim,
            "Speed (per 2 year)": self.speed * 2 * 365 * 24 * 3600,
            "Total Unclaimed TORCH": self.claimable_vested_token,
            "Total Withdrawable Boost": self.claimable_boost_token,
        }


# Start of the vesting process
print("* Start of the vesting process")
vesting = VestingBoost(initial_vesting=100)
vesting.boost(boost_amount=100)
current_status = vesting.get_current_state()
pprint(current_status)
print()

# 6 months after the start of the vesting process
print("* 6 months after the start of the vesting process")
vesting.adjust_time(additional_seconds=int((365 / 2) * 24 * 3600))
vesting.add_vesting(additional_vesting=200)
current_status = vesting.get_current_state()
pprint(current_status)
print()

# 1.5 year after the start of the vesting process
print("* 1.5 year after the start of the vesting process")
vesting.adjust_time(additional_seconds=int(365 * 24 * 3600))
current_status = vesting.get_current_state()
pprint(current_status)
print()

# 2 years after the start of the vesting process
print("* 2 years after the start of the vesting process")
vesting.adjust_time(additional_seconds=int(365 * 24 * 3600))
current_status = vesting.get_current_state()
pprint(current_status)
print()

vesting.add_vesting(additional_vesting=100)
vesting.boost(boost_amount=100)
current_status = vesting.get_current_state()
pprint(current_status)
