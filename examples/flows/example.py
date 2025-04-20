from prefect import flow


@flow(log_prints=True, description="An example flow", name="example-flow")
def main():
    print("I'm an example flow!")


if __name__ == "__main__":
    main()
