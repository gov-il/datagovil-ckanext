import ckan.plugins.interfaces as interfaces


class Ireport(interfaces.Interface):
    """
    Hook into report form
    """
    def mail_alter(self, mail_dict, data_dict):
        """
        Allow altering of email values
        For example, allow directing report form dependent on form values

        @param data_dict: form values
        @param mail_dict: dictionary of mail values, used in mailer.mail_recipient
        @return: altered mail_dict
        """
        return mail_dict