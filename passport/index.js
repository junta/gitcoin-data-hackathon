const PassportReader = require("@gitcoinco/passport-sdk-reader");
const fs = require("fs");
const { parse } = require("csv-parse/sync");
const { stringify } = require("csv-stringify/sync");

const readPassport = async (address) => {
  const CERAMIC_PASSPORT = "https://ceramic.passport-iam.gitcoin.co";
  const reader = new PassportReader.PassportReader(CERAMIC_PASSPORT, "1");

  //   const address = "0xeE22EE448a3A2b6B8F01A45da1476E2d01e24F3a";
  //   const address = "0xdffe6d135e4396f90ba66a1024bdeb6ef5df9276";
  const passport = await reader.getPassport(address);
  return passport;
};

const readPassportSample = async () => {
  const CERAMIC_PASSPORT = "https://ceramic.passport-iam.gitcoin.co";
  const reader = new PassportReader.PassportReader(CERAMIC_PASSPORT, "1");

  const address = "0xeE22EE448a3A2b6B8F01A45da1476E2d01e24F3a";

  const passport = await reader.getPassport(address);
  console.log(passport);
};

const filterValidStamps = (stamps) => {
  const currentTimestamp = Date.now();
  const gr15LastDay = Date.parse("2022-09-23T00:00:00.000Z");

  const filteredStamps = [];
  for (let i = 0; i < stamps?.length; i++) {
    const stamp = stamps[i];
    if (
      // select the first stamp when a provider is stored multiple times (should be the most recent)
      !stamps.slice(i + 1).find((s) => s.provider === stamp.provider) &&
      // check if stamp is not expired yet
      Date.parse(stamp.credential.expirationDate) > currentTimestamp &&
      Date.parse(stamp.credential.issuanceDate) < gr15LastDay
    ) {
      filteredStamps.push(stamp.provider);
    }
  }
  return filteredStamps;
};

const mainFunc = async () => {
  const inputData = fs.readFileSync("addresses.csv", { encoding: "utf8" });
  const parsedData = parse(inputData, { columns: true });

  //   console.log(parsedData[0]);
  for (record of parsedData) {
    console.log(record);

    // if (record.index < 80) continue;

    try {
      const passport = await readPassport(record.address);
      const validStamps = filterValidStamps(passport.stamps);
      record.valid_stamps_count = validStamps?.length;
      if (validStamps?.length) {
        record.stamp_providers = validStamps;
        record.issuance_date = passport.issuanceDate;
      }

      console.log(passport);

      const outputDataCsv = stringify(parsedData, { header: true });

      fs.writeFileSync("output.csv", outputDataCsv, { encoding: "utf8" });
    } catch (error) {
      console.error(error);
    }
  }
};

mainFunc();
// readPassportSample();
