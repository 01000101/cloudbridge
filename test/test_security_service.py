import itertools
import uuid

from test.helpers import ProviderTestBase
import test.helpers as helpers


class CloudSecurityServiceTestCase(ProviderTestBase):

    def __init__(self, methodName, provider):
        super(CloudSecurityServiceTestCase, self).__init__(
            methodName=methodName, provider=provider)

    def test_crud_key_pair_service(self):
        name = 'cbtestkeypairA-{0}'.format(uuid.uuid4())
        kp = self.provider.security.key_pairs.create(name=name)
        with helpers.cleanup_action(
            lambda:
                self.provider.security.key_pairs.delete(name=kp.name)
        ):
            found_kp = self.provider.security.key_pairs.find(name=name)
            self.assertTrue(
                found_kp == kp,
                "Find key pair did not return the expected key {0}."
                .format(name))
            recreated_kp = self.provider.security.key_pairs.create(name=name)
            self.assertTrue(
                recreated_kp == kp,
                "Recreating key pair did not return the expected key {0}."
                .format(name))
        kpl = self.provider.security.key_pairs.list()

        # check iteration
        iter_key_pairs = list(itertools.islice(
            self.provider.security.key_pairs,
            len(kpl)))
        self.assertListEqual(iter_key_pairs, kpl)

        found_kp = [k for k in kpl if k.name == name]
        self.assertTrue(
            len(found_kp) == 0,
            "Key pair {0} should have been deleted but still exists."
            .format(name))
        no_kp = self.provider.security.key_pairs.find(name='bogus_kp')
        self.assertTrue(
            no_kp is None,
            "Found a key pair {0} that should not exist?".format(no_kp))

    def test_key_pair(self):
        name = 'cbtestkeypairB-{0}'.format(uuid.uuid4())
        kp = self.provider.security.key_pairs.create(name=name)
        with helpers.cleanup_action(lambda: kp.delete()):
            kpl = self.provider.security.key_pairs.list()
            found_kp = [k for k in kpl if k.name == name]
            self.assertTrue(
                len(found_kp) == 1,
                "List key pairs did not return the expected key {0}."
                .format(name))
            self.assertTrue(
                kp.name in repr(kp),
                "repr(obj) should contain the object id so that the object"
                " can be reconstructed, but does not. eval(repr(obj)) == obj")
            self.assertIsNotNone(
                kp.material,
                "KeyPair material is empty but it should not be.")
            self.assertTrue(
                kp == kp,
                "The same key pair should be equal to self.")
        kpl = self.provider.security.key_pairs.list()
        found_kp = [k for k in kpl if k.name == name]
        self.assertTrue(
            len(found_kp) == 0,
            "Key pair {0} should have been deleted but still exists."
            .format(name))

    def test_crud_security_group_service(self):
        name = 'cbtestsecuritygroupA-{0}'.format(uuid.uuid4())
        sg = self.provider.security.security_groups.create(
            name=name, description=name)
        with helpers.cleanup_action(
            lambda:
                self.provider.security.security_groups.delete(group_id=sg.id)
        ):
            self.assertEqual(name, sg.description)

            sgl = self.provider.security.security_groups.get(
                group_names=[
                    sg.name])
            found_sg = [g for g in sgl if g.name == name]
            self.assertTrue(
                len(found_sg) == 1,
                "List security groups did not return the expected group {0}."
                .format(name))
        sgl = self.provider.security.security_groups.list()

        # check iteration
        iter_security_groups = list(itertools.islice(
            self.provider.security.security_groups,
            len(sgl)))
        self.assertListEqual(iter_security_groups, sgl)

        found_sg = [g for g in sgl if g.name == name]
        self.assertTrue(
            len(found_sg) == 0,
            "Security group {0} should have been deleted but still exists."
            .format(name))
        no_sg = self.provider.security.security_groups.get(
            group_ids=['bogus_sg'])
        self.assertTrue(
            len(no_sg) == 0,
            "Found a bogus security group?!?".format(no_sg))

    def test_security_group(self):
        """Test for proper creation of a security group."""
        name = 'cbtestsecuritygroupB-{0}'.format(uuid.uuid4())
        sg = self.provider.security.security_groups.create(
            name=name, description=name)
        with helpers.cleanup_action(lambda: sg.delete()):
            sg.add_rule(ip_protocol='tcp', from_port=1111, to_port=1111,
                        cidr_ip='0.0.0.0/0')
            found_rules = [rule for rule in sg.rules if
                           rule.cidr_ip == '0.0.0.0/0' and
                           rule.ip_protocol == 'tcp' and
                           rule.from_port == 1111 and
                           rule.to_port == 1111]
            self.assertTrue(
                len(found_rules) == 1,
                "Expected rule not found in security group: {0}".format(name))

            object_keys = (
                sg.rules[0].ip_protocol,
                sg.rules[0].from_port,
                sg.rules[0].to_port)
            self.assertTrue(
                all(str(key) in repr(sg.rules[0]) for key in object_keys),
                "repr(obj) should contain ip_protocol, form_port and to_port"
                " so that the object can be reconstructed, but does not."
                " eval(repr(obj)) == obj")
            self.assertTrue(
                sg == sg,
                "The same security groups should be equal?")
            self.assertFalse(
                sg != sg,
                "The same security groups should still be equal?")
        sgl = self.provider.security.security_groups.list()
        found_sg = [g for g in sgl if g.name == name]
        self.assertTrue(
            len(found_sg) == 0,
            "Security group {0} should have been deleted but still exists."
            .format(name))

    def test_security_group_group_role(self):
        """Test for proper creation of a security group rule."""
        name = 'cbtestsecuritygroupC-{0}'.format(uuid.uuid4())
        sg = self.provider.security.security_groups.create(
            name=name, description=name)
        with helpers.cleanup_action(lambda: sg.delete()):
            self.assertTrue(
                len(sg.rules) == 0,
                "Expected no security group group rule. Got {0}."
                .format(sg.rules))
            sg.add_rule(src_group=sg)
            self.assertTrue(
                sg.rules[0].group.name == name,
                "Expected security group rule name {0}. Got {1}."
                .format(name, sg.rules[0].group.name))
        sgl = self.provider.security.security_groups.list()
        found_sg = [g for g in sgl if g.name == name]
        self.assertTrue(
            len(found_sg) == 0,
            "Security group {0} should have been deleted but still exists."
            .format(name))
