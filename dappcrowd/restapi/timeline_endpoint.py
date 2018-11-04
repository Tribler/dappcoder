import json

from dappcrowd.restapi.root_endpoint import DAppCrowdEndpoint


class TimelineEndpoint(DAppCrowdEndpoint):

    def render_GET(self, request):
        trustchain = self.get_trustchain()
        all_blocks = sorted(trustchain.persistence.get_all_blocks(), key=lambda blk: blk.timestamp, reverse=True)
        timeline_list = []

        # Build a timeline with information
        for block in all_blocks:
            if block.type == 'devid_connection':
                timeline_list.append({
                    "type": "profile_import",
                    "platform": block.transaction['platform'],
                    "public_key": block.public_key.encode('hex'),
                    "username": self.get_trustchain().persistence.get_username(block.public_key),
                    "timestamp": block.timestamp
                })
            elif block.type == 'dappcoder_project':
                timeline_list.append({
                    "type": "created_job",
                    "public_key": block.public_key.encode('hex'),
                    "job_name": block.transaction['name'],
                    "username": self.get_trustchain().persistence.get_username(block.public_key),
                    "timestamp": block.timestamp
                })
            elif block.type == 'dappcoder_submission':
                submission = self.get_dappcrowd_overlay().persistence.get_submission(block.public_key, block.transaction['id'])
                timeline_list.append({
                    "type": "created_submission",
                    "public_key": block.public_key.encode('hex'),
                    "username": self.get_trustchain().persistence.get_username(block.public_key),
                    "timestamp": block.timestamp,
                    "job_name": submission['project_name']
                })
            elif block.type == 'devid_skill':
                if block.link_sequence_number:
                    timeline_list.append({
                        "type": "endorsement",
                        "public_key": block.public_key.encode('hex'),
                        "username": self.get_trustchain().persistence.get_username(block.public_key),
                        "endorsed_username": self.get_trustchain().persistence.get_username(block.link_public_key),
                        "timestamp": block.timestamp,
                        "skill_name": block.transaction['name']
                    })
                else:
                    timeline_list.append({
                        "type": "added_skill",
                        "public_key": block.public_key.encode('hex'),
                        "username": self.get_trustchain().persistence.get_username(block.public_key),
                        "timestamp": block.timestamp,
                        "skill_name": block.transaction['name']
                    })

        return json.dumps({"timeline": timeline_list})
