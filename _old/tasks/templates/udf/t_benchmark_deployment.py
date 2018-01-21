template_deployment = {
    "apiVersion": "v1",
    "kind": "DeploymentConfig",
    "metadata": {
        "name": "benchmark-job-8sfg564ssdfg",
        "labels": {
            "app": "benchmark-job-8sfg564ssdfg",
            "provider": "eodc",
            "project": "benchmark-job-8sfg564ssdfg",
            "version": "1.0.0"
        }
    },
    "spec": {
        "template": {
            "spec": {
                "containers": [
                    {
                        "livenessProbe": {
                            "timeoutSeconds": 1,
                            "initialDelaySeconds": 30,
                            "tcpSocket": {
                                "port": 1234
                            }
                        },
                        "image": "benchmark-job-8sfg564ssdfg",
                        "name": "benchmark-job-8sfg564ssdfg",
                        "securityContext": {
                            "privileged": False
                        },
                        "ports": [
                            {
                                "containerPort": 1234,
                                "name": "http",
                                "protocol": "TCP"
                            }
                        ],
                        "resources": {
                            "limits": {
                                "cpu": "300m",
                                "memory": "300Mi"
                            },
                            "requests": {
                                "cpu": "300m",
                                "memory": "300Mi"
                            }
                        }
                    },
                    {
                        "image": "google/cadvisor",
                        "imagePullPolicy": "Always",
                        "name": "cadvisor",
                        "ports": [
                            {
                                "containerPort": 8080,
                                "protocol": "TCP"
                            }
                        ],
                        "resources": {},
                        "terminationMessagePath": "/dev/termination-log",
                        "terminationMessagePolicy": "File"
                    }
                ]
            },
            "metadata": {
                "labels": {
                    "app": "benchmark-job-8sfg564ssdfg",
                    "project": "benchmark-job-8sfg564ssdfg",
                    "provider": "eodc",
                    "version": "1.0.0"
                }
            }
        },
        "replicas": 1,
        "selector": {
            "app": "benchmark-job-8sfg564ssdfg",
            "project": "benchmark-job-8sfg564ssdfg",
            "provider": "eodc"
        },
        "triggers": [
            {
                "type": "ConfigChange"
            },
            {
                "type": "ImageChange",
                "imageChangeParams": {
                    "automatic": True,
                    "containerNames": [
                        "benchmark-job-8sfg564ssdfg"
                    ],
                    "from": {
                        "kind": "ImageStreamTag",
                        "name": "benchmark-job-8sfg564ssdfg:latest"
                    }
                }
            }
        ]
    }
}