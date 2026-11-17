"""The seeded streams of the generator: fixed values, independence, rough shape."""

from __future__ import annotations

import statistics

from specfirst.gen.rng import Stream, seed_sha256


def test_a_stream_gives_the_same_numbers_on_every_machine_and_version():
    """These values are part of the generator: if they change, every study changes."""
    stream = Stream("seed", "a", 1)
    assert [stream.below(1000) for _ in range(5)] == [177, 318, 191, 209, 128]
    assert round(Stream("seed", "a", 1).uniform(), 12) == 0.16209357167
    other = Stream("seed", "b")
    assert other.between(3, 9) == 3
    assert other.choice(["x", "y", "z"]) == "z"
    assert other.shuffled(range(6)) == [3, 2, 0, 5, 4, 1]
    assert round(other.normal(10, 2), 9) == 10.487402569
    assert round(other.exponential(5), 9) == 1.287510443
    assert other.poisson(3.0) == 0


def test_streams_are_named_not_ordered():
    """A stream depends on its name alone: using another stream first changes nothing."""
    first = Stream("seed", "subject", 7).uniform()
    noise = Stream("seed", "subject", 6)
    for _ in range(100):
        noise.uniform()
    assert Stream("seed", "subject", 7).uniform() == first
    assert Stream("seed", "subject").child(7).uniform() == first
    assert Stream("seed", "subject", 8).uniform() != first
    assert Stream("other", "subject", 7).uniform() != first
    # The parts of a name do not run together: ("ab", "c") is not ("a", "bc").
    assert Stream("seed", "ab", "c").uniform() != Stream("seed", "a", "bc").uniform()


def test_the_distributions_have_their_shape():
    uniform = Stream("stat", "u")
    values = [uniform.uniform() for _ in range(20000)]
    assert all(0.0 <= value < 1.0 for value in values)
    assert abs(statistics.mean(values) - 0.5) < 0.01
    normal = Stream("stat", "n")
    values = [normal.normal(5, 2) for _ in range(20000)]
    assert abs(statistics.mean(values) - 5) < 0.05 and abs(statistics.pstdev(values) - 2) < 0.05
    poisson = Stream("stat", "p")
    assert abs(statistics.mean(poisson.poisson(2.5) for _ in range(20000)) - 2.5) < 0.05
    waiting = Stream("stat", "e")
    assert abs(statistics.mean(waiting.exponential(4) for _ in range(20000)) - 4) < 0.1


def test_choice_follows_its_weights_and_bounds_hold():
    stream = Stream("stat", "c")
    picks = [stream.choice("ab", (9.0, 1.0)) for _ in range(5000)]
    assert 0.87 < picks.count("a") / len(picks) < 0.93
    assert {stream.between(2, 4) for _ in range(200)} == {2, 3, 4}
    sample = stream.sample(range(10), 4)
    assert len(set(sample)) == 4 and set(sample) <= set(range(10))


def test_a_kit_names_the_hash_of_its_seed_never_the_seed():
    assert seed_sha256("gen-1a-1").startswith("77418314e8986b32")
    assert "gen-1a-1" not in seed_sha256("gen-1a-1")
