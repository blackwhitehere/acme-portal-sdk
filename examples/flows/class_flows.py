from prefect import flow


class ContainerClass:
    @flow(log_prints=True)
    def in_class_flow(self):
        print("This is an example flow in a class!")
