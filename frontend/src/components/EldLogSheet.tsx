import type { DailyLog, DutyEvent } from "../types/trip";

interface Props {
  log: DailyLog;
}

const STATUS_ROWS = [
  {
    key: "OFF",
    label: "Off Duty",
  },
  {
    key: "SB",
    label: "Sleeper Berth",
  },
  {
    key: "D",
    label: "Driving",
  },
  {
    key: "ON",
    label: "On Duty",
  },
] as const;

const LEFT_WIDTH = 120;
const RIGHT_WIDTH = 60;

const GRID_START_X = LEFT_WIDTH;
const GRID_WIDTH = 960;

const ROW_HEIGHT = 42;
const HEADER_HEIGHT = 42;
const GRAPH_HEIGHT =
  STATUS_ROWS.length * ROW_HEIGHT;

const SVG_WIDTH =
  LEFT_WIDTH + GRID_WIDTH + RIGHT_WIDTH;

const SVG_HEIGHT =
  HEADER_HEIGHT + GRAPH_HEIGHT + 10;


function minutesFromMidnight(
  dateString: string
) {
  const date = new Date(dateString);

  return (
    date.getHours() * 60 +
    date.getMinutes()
  );
}


function xForMinutes(
  minutes: number
) {
  return (
    GRID_START_X +
    (minutes / 1440) * GRID_WIDTH
  );
}


function rowY(
  status: string
) {
  const index =
    STATUS_ROWS.findIndex(
      (row) => row.key === status
    );

  return (
    HEADER_HEIGHT +
    index * ROW_HEIGHT +
    ROW_HEIGHT / 2
  );
}


function eventEndMinutes(
  event: DutyEvent
) {
  const start = new Date(event.start);
  const end = new Date(event.end);

  if (
    end.getDate() !== start.getDate() ||
    end.getMonth() !== start.getMonth() ||
    end.getFullYear() !== start.getFullYear()
  ) {
    return 1440;
  }

  return minutesFromMidnight(
    event.end
  );
}


export default function EldLogSheet({
  log,
}: Props) {
  return (
    <div className="eld-sheet">

      <div className="eld-header">

        <div>
          <span className="eld-eyebrow">
            DRIVER'S DAILY LOG
          </span>

          <h3>
            {new Date(
              `${log.date}T00:00:00`
            ).toLocaleDateString(
              undefined,
              {
                weekday: "long",
                month: "long",
                day: "numeric",
                year: "numeric",
              }
            )}
          </h3>
        </div>

        <div className="eld-mileage">
          <span>
            Miles Driven
          </span>

          <strong>
            {log.total_miles.toFixed(0)}
          </strong>
        </div>

      </div>


      <div className="eld-scroll">

        <svg
          viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
          className="eld-graph"
        >

          {/* Hour labels */}
          {Array.from(
            { length: 25 },
            (_, hour) => {
              const x =
                GRID_START_X +
                (hour / 24) *
                  GRID_WIDTH;

              return (
                <g key={hour}>
                  <line
                    x1={x}
                    y1={HEADER_HEIGHT}
                    x2={x}
                    y2={
                      HEADER_HEIGHT +
                      GRAPH_HEIGHT
                    }
                    className="eld-hour-line"
                  />

                  {hour < 24 && (
                    <text
                      x={
                        x +
                        GRID_WIDTH /
                          48
                      }
                      y={27}
                      textAnchor="middle"
                      className="eld-hour-text"
                    >
                      {hour === 0
                        ? "Mid"
                        : hour === 12
                          ? "Noon"
                          : hour}
                    </text>
                  )}
                </g>
              );
            }
          )}


          {/* 15-minute grid */}
          {Array.from(
            { length: 97 },
            (_, index) => {
              if (index % 4 === 0) {
                return null;
              }

              const x =
                GRID_START_X +
                (index / 96) *
                  GRID_WIDTH;

              return (
                <line
                  key={index}
                  x1={x}
                  y1={HEADER_HEIGHT}
                  x2={x}
                  y2={
                    HEADER_HEIGHT +
                    GRAPH_HEIGHT
                  }
                  className="eld-quarter-line"
                />
              );
            }
          )}


          {/* Duty status rows */}
          {STATUS_ROWS.map(
            (row, index) => {
              const y =
                HEADER_HEIGHT +
                index * ROW_HEIGHT;

              return (
                <g key={row.key}>
                  <rect
                    x={GRID_START_X}
                    y={y}
                    width={GRID_WIDTH}
                    height={ROW_HEIGHT}
                    className="eld-row"
                  />

                  <text
                    x={8}
                    y={
                      y +
                      ROW_HEIGHT / 2 +
                      5
                    }
                    className="eld-row-label"
                  >
                    {row.label}
                  </text>

                  <text
                    x={
                      GRID_START_X +
                      GRID_WIDTH +
                      RIGHT_WIDTH / 2
                    }
                    y={
                      y +
                      ROW_HEIGHT / 2 +
                      5
                    }
                    textAnchor="middle"
                    className="eld-total"
                  >
                    {log.totals[
                      row.key
                    ].toFixed(2)}
                  </text>
                </g>
              );
            }
          )}


          {/* Duty status trace */}
          {log.events.map(
            (event, index) => {
              const startMinutes =
                minutesFromMidnight(
                  event.start
                );

              const endMinutes =
                eventEndMinutes(event);

              const x1 =
                xForMinutes(
                  startMinutes
                );

              const x2 =
                xForMinutes(
                  endMinutes
                );

              const y =
                rowY(event.status);

              const nextEvent =
                log.events[index + 1];

              return (
                <g key={index}>

                  <line
                    x1={x1}
                    y1={y}
                    x2={x2}
                    y2={y}
                    className="eld-duty-line"
                  />

                  {nextEvent && (
                    <line
                      x1={x2}
                      y1={y}
                      x2={x2}
                      y2={rowY(
                        nextEvent.status
                      )}
                      className="eld-duty-line"
                    />
                  )}

                </g>
              );
            }
          )}

        </svg>

      </div>


      <div className="eld-summary">

        {STATUS_ROWS.map((row) => (
          <div
            key={row.key}
            className="eld-summary-item"
          >
            <span>
              {row.label}
            </span>

            <strong>
              {log.totals[
                row.key
              ].toFixed(2)} hrs
            </strong>
          </div>
        ))}

      </div>


      <div className="eld-remarks">

        <h4>Remarks</h4>

        {log.events
          .filter(
            (event) =>
              event.reason !==
              "Off duty"
          )
          .map(
            (event, index) => (
              <div
                className="remark-row"
                key={index}
              >
                <span>
                  {new Date(
                    event.start
                  ).toLocaleTimeString(
                    [],
                    {
                      hour: "2-digit",
                      minute: "2-digit",
                    }
                  )}
                </span>

                <strong>
                  {event.reason}
                </strong>

                {event.location && (
                  <p>
                    {event.location}
                  </p>
                )}
              </div>
            )
          )}

      </div>

    </div>
  );
}