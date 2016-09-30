from .spotify import Spotify10

POLICIES = {}
POLICIES['Spotify 1.0'] = Spotify10

def load_policy(name, section):
    """
    Load and return an instance of the policy with the given name.
    """

    try:
        policy = POLICIES[name]
    except KeyError:
        raise Exception('Unsupported policy (' + name + ')')

    return policy(section)
