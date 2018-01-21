template_job = {
  "kind": "Job",
  "apiVersion": "batch/v1",
  "metadata": {
    "name": "benchmark-job-8sfg564ssdfg"
  },
  "spec": {
    "activeDeadlineSeconds": 300,
    "parallelism": 1,
    "completions": 1,
    "template": {
      "metadata": {
        "labels": {
          "name": "benchmark-job-8sfg564ssdfg"
        }
      },
      "spec": {
        "containers": [
          {
            "name": "benchmark-job-8sfg564ssdfg",
            "image": "benchmark-job-8sfg564ssdfg:latest",
            "resources": {
              "limits": {
                "cpu": "300m",
                "memory": "300Mi"
              },
              "requests": {
                "cpu": "300m",
                "memory": "300Mi"
              }
            },
            "volumeMounts": [
              {
                "name": "vol-eodc",
                "mountPath": "/eodc"
              }
            ]
          }
        ],
        "securityContext": {
          "supplementalGroups": [
            60028,
            65534
          ]
        },
        "restartPolicy": "OnFailure",
        "volumes": [
          {
            "name": "vol-eodc",
            "persistentVolumeClaim": {
              "claimName": "pvc-eodc"
            }
          }
        ]
      }
    }
  }
}