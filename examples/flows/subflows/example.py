from prefect import flow


@flow(
    log_prints=True,
    description="A nested flow",
)
def nested_flow():
    print("I'm a flow inside a subdirectory!")


if __name__ == "__main__":
    nested_flow()
