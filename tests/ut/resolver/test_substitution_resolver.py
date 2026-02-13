import pytest

from hocon.exceptions import HOCONSubstitutionCycleError
from hocon.resolver._substitution import Substitution, SubstitutionStatus
from hocon.resolver._substitution_resolver import SubstitutionResolver
from hocon.resolver._resolver import Resolver
from hocon.unresolved import UnresolvedSubstitution
from hocon.parser import parse


def test_error_when_fallback_resolving():
    """When a substitution is in FALLBACK_RESOLVING state and has been triggered to be resolved again, it should raise a HOCONSubstitutionCycleError.
    It is a Unit Test, since I haven't figured out any way to trigger this exception from the public interface.
    """
    parsed = parse("""a: ${b}""")
    sub: UnresolvedSubstitution = parsed["a"][0]
    resolver = Resolver(parsed)
    sub_resolver = SubstitutionResolver(parsed, resolver)
    sub_resolver.subs[sub.id_] = Substitution(status=SubstitutionStatus.FALLBACK_RESOLVING)
    with pytest.raises(HOCONSubstitutionCycleError, match=r"Could not resolve \${b}"):
        sub_resolver(sub)
